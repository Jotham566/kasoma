"""Read-only, allowlisted self-service export; never serialize ORM rows wholesale."""

from collections.abc import Callable, Generator, Iterator
from contextlib import ExitStack, closing
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, Text, cast, exists, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import InstrumentedAttribute, Session

from services.assessment_contracts import GradeView
from services.content_contracts import DraftDocument
from services.data_export_encoding import ExportRecord, encode_records
from services.data_request_contracts import DataExportBundle
from services.domain.assessment import (
    AssessmentSession,
    Attempt,
    Grade,
    HintUse,
    Reassessment,
    SessionItem,
)
from services.domain.content import ItemVersion
from services.domain.curriculum import Competency, Concept, Subject, Topic
from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.domain.flags import ContentFlag
from services.domain.grading_work import GradingHistory, GradingWorkRow
from services.domain.identity import Consent, Identifier, IdentityEvent, LearnerSubject, User
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.domain.messaging import (
    ChannelLink,
    ConversationState,
    InboundMessage,
    OutboundMessage,
)
from services.identity import IdentityError, IdentityService
from services.mastery_engine import Estimate, Evidence

MAX_RECORDS = 10_000
EXCLUSIONS = [
    "Authentication credentials, OTPs, lookup hashes and internal security records.",
    "Guardian contact/name/evidence and staff identities or internal notes.",
    "Answer keys, rubrics, worked solutions, future assignments and selection internals.",
    "Unfinished or abandoned diagnostic grades and calculations depending on sealed evidence.",
    "Content-owned feedback, operational audit internals and third-party records "
    "need separate review.",
]
BATCH_SIZE = 100
CHUNK_BYTES = 16_384


class ProjectionReader:
    """Bound ORM hydration and close every cursor, including projection failures."""

    def __init__(
        self,
        db: Session,
        stack: ExitStack,
        *,
        record_limit: int | None = None,
        checkpoint: Callable[[], None] | None = None,
    ) -> None:
        if record_limit is not None and not 1 <= record_limit <= 100_000:
            raise ValueError("Invalid projection record limit")
        self.db, self.stack = db, stack
        self.remaining = MAX_RECORDS if record_limit is None else record_limit
        self.checkpoint = checkpoint or (lambda: None)

    def rows(self, query: Select[Any], *, scalar: bool = True) -> Iterator[Any]:
        self.checkpoint()
        result = self.db.execute(
            query.limit(self.remaining + 1).execution_options(yield_per=BATCH_SIZE)
        )
        self.stack.callback(result.close)
        try:
            for row in result:
                self.checkpoint()
                self.remaining -= 1
                if self.remaining < 0:
                    raise IdentityError("EXPORT_LIMIT_REACHED", 409)
                yield row[0] if scalar else row
        finally:
            result.close()


def project(identity: IdentityService, db: Session, actor: UUID, target: UUID) -> DataExportBundle:
    # Compatibility for existing internal readers; HTTP generation supplies its byte cap.
    with closing(encoded_project(identity, db, actor, target, max_bytes=None)) as chunks:
        return DataExportBundle.model_validate_json(b"".join(chunks))


def encoded_project(
    identity: IdentityService,
    db: Session,
    actor: UUID,
    target: UUID,
    *,
    max_bytes: int | None,
    record_limit: int | None = None,
    chunk_bytes: int | None = None,
    checkpoint: Callable[[], None] | None = None,
) -> Generator[bytes, None, None]:
    size = CHUNK_BYTES if chunk_bytes is None else chunk_bytes
    if not 1 <= size <= 65_536:
        raise ValueError("Invalid projection chunk size")

    def metadata() -> dict[str, Any]:
        # Preserve generation/completion time at the end of the read, as in ADR-028.
        return DataExportBundle(
            request_id=target, generated_at=identity.clock(), exclusions=EXCLUSIONS, records={}
        ).model_dump(mode="json", exclude={"records"})

    with ExitStack() as stack:
        source = _records(
            identity,
            db,
            actor,
            ProjectionReader(db, stack, record_limit=record_limit, checkpoint=checkpoint),
        )
        with closing(encode_records(source, metadata, max_bytes=max_bytes)) as chunks:
            pending = bytearray()
            for chunk in chunks:
                view = memoryview(chunk)
                while view:
                    room = size - len(pending)
                    pending.extend(view[:room])
                    view = view[room:]
                    if len(pending) == size:
                        yield bytes(pending)
                        pending.clear()
            if pending:
                yield bytes(pending)


def _records(
    identity: IdentityService, db: Session, actor: UUID, reader: ProjectionReader
) -> Iterator[ExportRecord]:
    rows = reader.rows
    owned_attempts = select(Attempt.id).where(Attempt.learner_id == actor)
    released = or_(AssessmentSession.kind != "DIAGNOSTIC", AssessmentSession.status == "COMPLETED")
    visible = (
        select(Attempt.id)
        .join(SessionItem, SessionItem.id == Attempt.session_item_id)
        .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
        .where(Attempt.learner_id == actor, AssessmentSession.learner_id == actor, released)
    )
    evidence_query = select(MasteryEvidence).where(
        MasteryEvidence.learner_id == actor, MasteryEvidence.attempt_id.in_(visible)
    )

    def fields(row: Any, names: str) -> dict[str, Any]:
        result = {}
        for name in names.split():
            value = getattr(row, name)
            result[name] = (
                value.isoformat()
                if isinstance(value, (date, datetime))
                else str(value)
                if isinstance(value, UUID)
                else value
            )
        return result

    user = db.get(User, actor)
    if user is None:
        raise IdentityError("RESOURCE_NOT_FOUND", 404)
    yield ("profile", None)
    yield (
        "profile",
        fields(user, "id status birth_date created_at")
        | {"display_name": identity.decrypt(user.display_name) if user.display_name else None},
    )
    yield ("identifiers", None)
    for r in rows(select(Identifier).where(Identifier.user_id == actor).order_by(Identifier.id)):
        yield (
            "identifiers",
            fields(r, "type verified_at")
            | {"value": identity.decrypt(r.normalized_value_encrypted)},
        )
    yield ("subjects", None)
    for r in rows(
        select(Subject)
        .join(LearnerSubject, LearnerSubject.subject_id == Subject.id)
        .where(LearnerSubject.user_id == actor)
        .order_by(Subject.id)
    ):
        yield ("subjects", fields(r, "id name"))
    yield ("consents", None)
    for r in rows(select(Consent).where(Consent.user_id == actor).order_by(Consent.id)):
        yield ("consents", fields(r, "id consent_type basis policy_version granted_at revoked_at"))
    sessions = select(AssessmentSession).where(AssessmentSession.learner_id == actor)
    yield ("sessions", None)
    for r in rows(sessions.order_by(AssessmentSession.id)):
        yield (
            "sessions",
            fields(
                r,
                "id subject_id topic_id kind status item_count reason plan_version "
                "started_at expires_at completed_at",
            ),
        )
    # Preserve ADR-028 accounting for distinct lookup rows without retaining ID maps.
    lookup_columns: list[tuple[InstrumentedAttribute[UUID], InstrumentedAttribute[UUID]]] = [
        (SessionItem.id, Attempt.session_item_id),
        (ItemVersion.id, Attempt.item_version_id),
    ]
    for key, reference in lookup_columns:
        lookup = select(reference).where(Attempt.learner_id == actor)
        for _ in rows(select(key).where(key.in_(lookup)).order_by(key)):
            pass
    answers = (
        select(Attempt, SessionItem.session_id, ItemVersion.document, released)
        .join(SessionItem, SessionItem.id == Attempt.session_item_id)
        .join(ItemVersion, ItemVersion.id == Attempt.item_version_id)
        .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
        .where(Attempt.learner_id == actor, AssessmentSession.learner_id == actor)
        .order_by(Attempt.id)
    )
    yield ("answers", None)
    for a, session_id, document, grade_released in rows(answers, scalar=False):
        doc = DraftDocument.model_validate(document)
        yield (
            "answers",
            fields(a, "id item_version_id submitted_at hint_count highest_hint_level channel")
            | {
                "session_id": str(session_id),
                "response": a.response
                if a.response is not None
                else {"type": "SINGLE_CHOICE", "choice_id": a.choice_id},
                "question": {
                    "prompt": doc.prompt,
                    "choices": [c.model_dump() for c in doc.choices],
                },
                "grade_released": grade_released,
            },
        )
    yield ("grading_work", None)
    for work in rows(
        select(GradingWorkRow)
        .where(GradingWorkRow.attempt_id.in_(visible))
        .order_by(GradingWorkRow.attempt_id)
    ):
        yield ("grading_work", fields(work, "attempt_id status queued_at claimed_at finished_at"))
    yield ("grading_history", None)
    for history in rows(
        select(GradingHistory)
        .where(GradingHistory.attempt_id.in_(visible))
        .order_by(GradingHistory.attempt_id, GradingHistory.revision)
    ):
        yield (
            "grading_history",
            fields(history, "id attempt_id revision")
            | {
                name: history.snapshot[name]
                for name in ("status", "queued_at", "claimed_at", "finished_at")
            },
        )
    yield ("grades", None)
    for g in rows(select(Grade).where(Grade.attempt_id.in_(visible)).order_by(Grade.attempt_id)):
        result = GradeView.model_validate(g.result)
        yield (
            "grades",
            fields(
                result,
                "attempt_id item_version_id status score points_awarded points_possible "
                "confidence method grader_version",
            ),
        )
    yield ("hints", None)
    for r in rows(select(HintUse).where(HintUse.learner_id == actor).order_by(HintUse.id)):
        yield ("hints", fields(r, "session_item_id level phase created_at"))
    yield ("mastery_evidence", None)
    for r in rows(evidence_query.order_by(MasteryEvidence.id)):
        yield ("mastery_evidence", Evidence.model_validate(r.snapshot).model_dump(mode="json"))
    # Validate sealed snapshots and count them, but never disclose derived hidden grades.
    visible_text = visible.with_only_columns(cast(Attempt.id, Text))
    projections: list[tuple[str, InstrumentedAttribute[dict[str, Any]], Select[Any]]] = [
        (
            "mastery_estimates",
            MasteryEstimate.snapshot,
            select(MasteryEstimate)
            .where(MasteryEstimate.learner_id == actor)
            .order_by(MasteryEstimate.concept_id, MasteryEstimate.competency_id),
        ),
        (
            "mastery_history",
            MasteryHistory.snapshot,
            select(MasteryHistory)
            .where(
                MasteryHistory.evidence_id.in_(evidence_query.with_only_columns(MasteryEvidence.id))
            )
            .order_by(MasteryHistory.id),
        ),
    ]
    for section, snapshot, query in projections:
        inputs = func.jsonb_array_elements_text(
            cast(snapshot, JSONB)["input_attempt_ids"]
        ).table_valued("value")
        withheld = exists(select(1).select_from(inputs).where(inputs.c.value.not_in(visible_text)))
        yield (section, None)
        for row, sealed in rows(query.add_columns(withheld), scalar=False):
            estimate = Estimate.model_validate(row.snapshot)
            if not sealed:
                yield (section, estimate.model_dump(mode="json"))
    yield ("reports", None)
    for r in rows(
        select(ContentFlag).where(ContentFlag.reporter_id == actor).order_by(ContentFlag.id)
    ):
        yield (
            "reports",
            fields(r, "id attempt_id item_version_id category created_at")
            | {"comment": identity.decrypt(r.comment_encrypted)},
        )
    yield ("reassessments", None)
    for r in rows(
        select(Reassessment)
        .where(Reassessment.original_attempt_id.in_(owned_attempts))
        .order_by(Reassessment.original_attempt_id)
    ):
        yield ("reassessments", fields(r, "original_attempt_id session_id basis elapsed_seconds"))
    yield ("data_requests", None)
    for r in rows(select(DataRequest).where(DataRequest.user_id == actor).order_by(DataRequest.id)):
        yield ("data_requests", fields(r, "id kind created_at completed_at retention_due_at"))
    yield ("export_jobs", None)
    job_fields = "request_id status created_at queued_at updated_at finished_at attempts failure"
    for r in rows(
        select(*(getattr(ExportJob, name) for name in job_fields.split()))
        .join(DataRequest, DataRequest.id == ExportJob.request_id)
        .where(DataRequest.user_id == actor)
        .order_by(ExportJob.request_id),
        scalar=False,
    ):
        yield ("export_jobs", fields(r, job_fields))
    yield ("export_copies", None)
    copy_fields = "request_id created_at published_at expires_at size"
    for r in rows(
        select(*(getattr(ExportGeneration, name) for name in copy_fields.split()))
        .join(DataRequest, DataRequest.id == ExportGeneration.request_id)
        .where(DataRequest.user_id == actor)
        .order_by(ExportGeneration.id),
        scalar=False,
    ):
        yield ("export_copies", fields(r, copy_fields))
    yield ("channel_links", None)
    for r in rows(select(ChannelLink).where(ChannelLink.user_id == actor).order_by(ChannelLink.id)):
        yield (
            "channel_links",
            fields(r, "id status revision linked_at opted_out_at")
            | {
                "identifier": identity.decrypt(r.external_identifier_encrypted)
                if r.external_identifier_encrypted
                else None
            },
        )
    yield ("channel_conversations", None)
    for r in rows(
        select(ConversationState)
        .where(ConversationState.actor_id == actor)
        .order_by(ConversationState.link_id)
    ):
        yield ("channel_conversations", fields(r, "link_id session_id updated_at expires_at"))
    yield ("channel_inbound", None)
    for r in rows(
        select(InboundMessage).where(InboundMessage.actor_id == actor).order_by(InboundMessage.id)
    ):
        yield ("channel_inbound", fields(r, "id command status received_at processed_at"))
    yield ("channel_outbound", None)
    for r in rows(
        select(OutboundMessage)
        .where(OutboundMessage.actor_id == actor)
        .order_by(OutboundMessage.id)
    ):
        yield ("channel_outbound", fields(r, "id template status created_at sent_at"))
    yield ("account_events", None)
    for r in rows(
        select(IdentityEvent)
        .where(
            IdentityEvent.user_id == actor,
            IdentityEvent.type.not_in(["legal_hold.created", "legal_hold.released"]),
        )
        .order_by(IdentityEvent.id)
    ):
        yield ("account_events", fields(r, "type created_at"))
    # Only referenced taxonomy names; never content keys or future assignments.
    concepts = select(Concept).where(
        Concept.id.in_(evidence_query.with_only_columns(MasteryEvidence.concept_id))
    )
    yield ("concepts", None)
    for r in rows(concepts.order_by(Concept.id)):
        yield ("concepts", fields(r, "id topic_id name"))
    topic_ids = sessions.with_only_columns(AssessmentSession.topic_id).union(
        concepts.with_only_columns(Concept.topic_id)
    )
    yield ("topics", None)
    for r in rows(select(Topic).where(Topic.id.in_(topic_ids)).order_by(Topic.id)):
        yield ("topics", fields(r, "id subject_id name"))
    yield ("competencies", None)
    for r in rows(
        select(Competency)
        .where(Competency.id.in_(evidence_query.with_only_columns(MasteryEvidence.competency_id)))
        .order_by(Competency.id)
    ):
        yield ("competencies", fields(r, "id name"))
