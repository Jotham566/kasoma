"""One leased job: no model work under locks; atomic authorized score or neutral outcome."""

from collections.abc import Callable
from dataclasses import dataclass, field
from time import monotonic
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_outcomes import response_projection, result_binding
from services.domain.assessment import AssessmentSession, Attempt, Grade, SessionItem
from services.domain.content import ItemVersion
from services.domain.grading_audits import GradingPublicationCounter
from services.domain.grading_work import GradingWorkRow
from services.grading_band_store import locked
from services.grading_band_store import snapshot as band_snapshot
from services.grading_publications import publish
from services.grading_work_store import apply, claim_next, expire_due, finish_neutral, snapshot
from services.identity import IdentityError
from services.mastery import reconcile
from services.providers import FakeModelProvider, ModelGateway, ModelResult, ModelTask
from services.rubric_grade_projection import project_candidate
from services.rubric_grade_protection import protect_result
from services.short_text_eligibility import AuditState, eligibility
from services.short_text_orchestration import RehearsalBudget, rehearse_short_text
from services.short_text_validation import ShortTextCandidate, SyntheticRubricContext
from services.short_text_workflow import expire_work, finish_work

SafetyAuthority = Callable[[SyntheticRubricContext, str], bool]


@dataclass(frozen=True)
class Material:
    attempt_id: UUID
    band_id: UUID
    context: SyntheticRubricContext = field(repr=False)
    response: str = field(repr=False)


class VersionedGateway:
    def __init__(
        self,
        gateway: ModelGateway,
        model_version: str,
        authorize: Callable[[], None],
        deadline: float,
    ):
        self.gateway, self.model_version = gateway, model_version
        self.authorize, self.deadline = authorize, deadline

    def execute(self, task: ModelTask) -> ModelResult:
        self.authorize()
        remaining = int((self.deadline - monotonic()) * 1000)
        if remaining <= 0:
            raise ValueError("Model budget expired before dispatch")
        task = task.model_copy(update={"timeout_ms": min(task.timeout_ms, remaining)})
        result = self.gateway.execute(task)
        if result.provider != "fake" or result.model != self.model_version:
            raise ValueError("Model provenance unavailable")
        return result


class ShortTextProcessor:
    def __init__(
        self,
        service: AssessmentService,
        gateway: FakeModelProvider | None = None,
        safety: SafetyAuthority | None = None,
    ):
        self.service = service
        self.identity = service.identity
        self.gateway = gateway or FakeModelProvider()
        # No real injection/safety/domain approval is invented by default startup.
        self.safety = safety

    def material(self, db: Session, attempt_id: UUID, claim_id: UUID) -> Material | None:
        attempt = db.get(Attempt, attempt_id)
        if attempt is None or not attempt.response or attempt.response.get("type") != "SHORT_TEXT":
            return None
        item = db.get(SessionItem, attempt.session_item_id)
        if item is None or item.grading_band_id is None:
            return None
        session = db.get(AssessmentSession, item.session_id)
        if session is None or session.status not in {"ACTIVE", "COMPLETED"}:
            return None
        self.service.authorize_actor(db, attempt.learner_id, session.subject_id)
        work = db.get(GradingWorkRow, attempt_id, populate_existing=True)
        if (
            work is None
            or work.claim_id != claim_id
            or work.status != "RUNNING"
            or (work.lease_until is None or self.identity.clock() >= work.lease_until)
        ):
            return None
        version = self.service.content.assessment_version(
            db, attempt.item_version_id, session.subject_id, assigned_band_id=item.grading_band_id
        )
        band = self.service.short_text.band_for(db, version)
        if band is None or band.id != item.grading_band_id:
            return None
        response = response_projection(self.identity, attempt)["text"]
        if not isinstance(response, str):
            return None
        counter = db.get(GradingPublicationCounter, band.id, populate_existing=True)
        if counter is None:
            return None
        # There is no completed-review table in this intermediate implementation.
        # Pending assignments are counted only as assigned, never completed/correct.
        audit = AuditState(
            band_id=band.id,
            returned_grades=counter.returned_grades,
            assigned_audits=counter.assigned_audits,
            disabled=not band.enabled,
        )
        if (
            eligibility(
                band=band_snapshot(band),
                scope=self.service.short_text.scope(db, version),
                response_characters=len(response),
                audit=audit,
                now=self.identity.clock(),
            )
            != "ELIGIBLE_CANDIDATE"
        ):
            return None
        settings = self.identity.settings
        if (
            settings.model_provider != "fake"
            or settings.short_text_prompt_version != "synthetic-short-text-dual-pass-v2"
            or settings.short_text_configuration_version != "short-text-runtime-v1"
        ):
            return None
        return Material(attempt.id, band.id, self.service.short_text.context(version), response)

    def process_one(self) -> bool:
        with Session(self.identity.engine) as db, db.begin():
            expire_due(db, self.identity.clock())
            work = claim_next(db, self.identity.clock())
            correlation = (
                db.scalar(
                    select(GradingWorkRow.correlation_id).where(
                        GradingWorkRow.attempt_id == work.attempt_id
                    )
                )
                if work is not None
                else None
            )
        if work is None or work.claim_id is None:
            return False
        attempt_id, claim_id = work.attempt_id, work.claim_id
        candidate: ShortTextCandidate | None = None
        failed = False
        try:
            with Session(self.identity.engine) as db, db.begin():
                material = self.material(db, work.attempt_id, work.claim_id)
            # Immutable input has been captured; all DB locks are released before inference.
            if (
                material is not None
                and self.safety is not None
                and (self.safety(material.context, material.response) is True)
            ):

                def authorize_dispatch() -> None:
                    with Session(self.identity.engine) as dispatch_db, dispatch_db.begin():
                        current = self.material(dispatch_db, attempt_id, claim_id)
                        if (
                            current is None
                            or self.safety is None
                            or (self.safety(current.context, current.response) is not True)
                        ):
                            raise ValueError("Current grading authority unavailable")

                result = rehearse_short_text(
                    VersionedGateway(
                        self.gateway,
                        self.identity.settings.short_text_model_version,
                        authorize_dispatch,
                        monotonic() + 5,
                    ),
                    context=material.context,
                    response=material.response,
                    flagged=False,
                    budget=RehearsalBudget(),
                    request_id=correlation,
                )
                candidate = result.candidate
                failed = result.reason in {
                    "PROVIDER_FAILURE",
                    "PROVIDER_FALLBACK",
                    "BUDGET",
                    "VALIDATION_FAILED",
                }
        except Exception:
            failed = True
        self.finish(work.attempt_id, work.claim_id, candidate, failed=failed)
        return True

    def finish(
        self,
        attempt_id: UUID,
        claim_id: UUID,
        candidate: ShortTextCandidate | None,
        *,
        failed: bool = False,
    ) -> None:
        with Session(self.identity.engine) as db, db.begin():
            attempt = db.get(Attempt, attempt_id)
            if attempt is None:
                return
            self.identity.lock(db, str(attempt.learner_id))
            row = db.scalar(
                select(GradingWorkRow)
                .where(GradingWorkRow.attempt_id == attempt_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if row is None or row.claim_id != claim_id or row.status != "RUNNING":
                return
            expired = expire_work(snapshot(row), self.identity.clock())
            if expired.status != "RUNNING":
                apply(db, row, expired)
                return
            item = db.get(SessionItem, attempt.session_item_id)
            # Take the exclusive band lock before policy's shared lookup: avoid lock upgrades.
            if item is not None and item.grading_band_id is not None:
                locked(db, item.grading_band_id)
            material = None
            if candidate is not None:
                try:
                    material = self.material(db, attempt_id, claim_id)
                    if material is not None and (
                        self.safety is None
                        or self.safety(material.context, material.response) is not True
                    ):
                        material = None
                except (IdentityError, ValueError):
                    material = None
            if candidate is None or material is None:
                finish_neutral(db, attempt_id, claim_id, self.identity.clock(), failed=failed)
                self.complete_diagnostic(db, attempt, row.correlation_id)
                return
            projected = project_candidate(
                attempt_id=attempt.id,
                candidate=candidate,
                context=material.context,
                response=material.response,
                hint_count=attempt.hint_count,
                highest_hint_level=attempt.highest_hint_level,
            ).model_copy(update={"mastery_update_status": "COMPLETED"})
            stored = protect_result(projected, result_binding(db, attempt), self.identity)
            version = db.get(ItemVersion, attempt.item_version_id)
            if version is None:
                raise ValueError("Pinned item unavailable")
            db.add(
                Grade(
                    attempt_id=attempt.id,
                    item_version_id=attempt.item_version_id,
                    answer_specification_hash=version.content_hash,
                    result=stored.model_dump(mode="json"),
                )
            )
            db.flush()
            publish(db, material.band_id, attempt.id, self.identity.clock())
            apply(
                db,
                row,
                finish_work(snapshot(row), self.identity.clock(), claim_id, outcome="GRADED"),
            )
            reconcile(db, attempt.learner_id, self.identity.clock())
            if item is None:
                raise ValueError("Pinned assignment unavailable")
            self.service.event(
                db, item.session_id, "attempt.graded", row.correlation_id, attempt.id
            )
            self.service.event(
                db,
                item.session_id,
                "mastery.updated",
                row.correlation_id,
                attempt.id,
                hint_count=attempt.hint_count,
                highest_hint_level=attempt.highest_hint_level,
            )
            session = db.get(AssessmentSession, item.session_id)
            if session is not None and session.kind == "REASSESSMENT":
                self.service.event(
                    db, session.id, "reassessment.completed", row.correlation_id, attempt.id
                )
            self.complete_diagnostic(db, attempt, row.correlation_id)

    def complete_diagnostic(self, db: Session, attempt: Attempt, request: UUID) -> None:
        item = db.get(SessionItem, attempt.session_item_id)
        session = db.get(AssessmentSession, item.session_id) if item else None
        if session is not None and session.kind == "DIAGNOSTIC":
            try:
                self.service.authorize_actor(db, attempt.learner_id, session.subject_id)
            except IdentityError:
                return
            self.service.diagnostics.complete_if_ready(db, session, request)
