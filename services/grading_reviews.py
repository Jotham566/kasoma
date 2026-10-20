"""Independent blinded synthetic review; immutable points never override learner grades."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_outcomes import response_projection
from services.content_contracts import DraftDocument
from services.domain.assessment import AssessmentSession, Attempt, SessionItem
from services.domain.content import AuditLog, Item, ItemVersion
from services.domain.grading_audits import (
    GradingAuditAssignment,
    GradingAuditReview,
    GradingPublication,
    GradingPublicationCounter,
    GradingReviewCounter,
)
from services.grading_band_store import locked
from services.grading_review_contracts import (
    AuditQueueEntry,
    AuditQueuePage,
    AuditReviewInput,
    AuditReviewReceipt,
    BlindedReviewTask,
)
from services.identity import IdentityError, IdentityService
from services.short_text_eligibility import AUDIT_WINDOW, AuditOutcome, AuditState
from services.staff import authorize


def audit_state(db: Session, band_id: UUID, *, disabled: bool, now: datetime) -> AuditState:
    publication = db.get(GradingPublicationCounter, band_id, populate_existing=True)
    counter = db.get(GradingReviewCounter, band_id, populate_existing=True)
    if publication is None or counter is None:
        raise ValueError("Grading audit state unavailable")
    rows = list(
        db.execute(
            select(GradingAuditReview, GradingAuditAssignment.attempt_id)
            .join(GradingAuditAssignment, GradingAuditAssignment.id == GradingAuditReview.id)
            .where(GradingAuditReview.band_id == band_id)
            .order_by(GradingAuditReview.completion_ordinal.desc())
            .limit(AUDIT_WINDOW)
        )
    )
    if any(row.completed_at > now for row, _ in rows):
        raise ValueError("Future audit state unavailable")
    return AuditState(
        band_id=band_id,
        returned_grades=publication.returned_grades,
        assigned_audits=publication.assigned_audits,
        completed_audits=counter.completed_audits,
        disabled=disabled,
        recent=tuple(
            AuditOutcome(
                grade_id=attempt_id,
                exact=row.exact_agreement,
                critical_error=row.critical_error != "NONE",
                completed_at=row.completed_at,
            )
            for row, attempt_id in reversed(rows)
        ),
    )


class GradingReviewService:
    def __init__(self, identity: IdentityService):
        self.identity = identity

    def actor(self, db: Session, token: str) -> UUID:
        return authorize(self.identity, db, token, {"ACADEMIC_REVIEWER"}, recent=True)[0]

    def audit(self, db: Session, actor: UUID, target: UUID, action: str, request: UUID) -> None:
        db.add(
            AuditLog(
                id=uuid4(),
                actor_id=actor,
                target_id=target,
                action=action,
                reason="Independent synthetic grading review",
                request_id=request,
                created_at=self.identity.clock(),
                before_hash=None,
                after_hash=None,
            )
        )

    def material(
        self, db: Session, actor: UUID, target: UUID, token: str
    ) -> tuple[GradingAuditAssignment, GradingPublication, Attempt, ItemVersion]:
        row = db.execute(
            select(
                GradingAuditAssignment, GradingPublication, Attempt, ItemVersion, AssessmentSession
            )
            .join(
                GradingPublication,
                GradingPublication.attempt_id == GradingAuditAssignment.attempt_id,
            )
            .join(Attempt, Attempt.id == GradingPublication.attempt_id)
            .join(ItemVersion, ItemVersion.id == Attempt.item_version_id)
            .join(Item, Item.id == ItemVersion.item_id)
            .join(SessionItem, SessionItem.id == Attempt.session_item_id)
            .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
            .where(
                GradingAuditAssignment.id == target,
                Attempt.learner_id != actor,
                ItemVersion.author_id != actor,
                Item.author_id != actor,
                ItemVersion.synthetic.is_(True),
                ItemVersion.document["response_type"].as_string() == "SHORT_TEXT",
            )
        ).first()
        if row is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        assignment, publication, attempt, version, session = row
        # Stable account order precedes the band. Role revocation uses the same
        # reviewer account lock, avoiding extra write privileges on the role table.
        for account in sorted({actor, attempt.learner_id}, key=str):
            self.identity.lock_user(db, account)
        if self.actor(db, token) != actor:
            raise IdentityError("AUTH_REQUIRED", 401)
        AssessmentService(self.identity).authorize_actor(db, attempt.learner_id, session.subject_id)
        if session.kind == "DIAGNOSTIC" and session.status != "COMPLETED":
            raise IdentityError("FORBIDDEN", 403)
        return assignment, publication, attempt, version

    def list(
        self, token: str, cursor: UUID | None = None, limit: int = 20, request: UUID | None = None
    ) -> AuditQueuePage:
        if not 1 <= limit <= 50:
            raise IdentityError("VALIDATION_FAILED", 422)
        with self.identity.transaction() as db:
            actor = self.actor(db, token)
            if not self.identity.rate(db, f"grading-audit-queue:{actor}", 60, 60):
                raise IdentityError("USAGE_LIMIT_REACHED", 429)
            query = (
                select(GradingAuditAssignment.id)
                .join(Attempt, Attempt.id == GradingAuditAssignment.attempt_id)
                .join(ItemVersion, ItemVersion.id == Attempt.item_version_id)
                .join(Item, Item.id == ItemVersion.item_id)
                .join(SessionItem, SessionItem.id == Attempt.session_item_id)
                .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
                .where(
                    ~select(GradingAuditReview.id)
                    .where(GradingAuditReview.id == GradingAuditAssignment.id)
                    .exists(),
                    Attempt.learner_id != actor,
                    ItemVersion.author_id != actor,
                    Item.author_id != actor,
                    ItemVersion.synthetic.is_(True),
                    ItemVersion.document["response_type"].as_string() == "SHORT_TEXT",
                    or_(
                        AssessmentSession.kind != "DIAGNOSTIC",
                        AssessmentSession.status == "COMPLETED",
                    ),
                )
                .order_by(GradingAuditAssignment.id)
                .limit(limit + 1)
            )
            if cursor is not None:
                query = query.where(GradingAuditAssignment.id > cursor)
            ids = list(db.scalars(query))
            self.audit(db, actor, actor, "grading_review.queue_read", request or uuid4())
            return AuditQueuePage(
                data=[AuditQueueEntry(id=target) for target in ids[:limit]],
                next_cursor=ids[limit - 1] if len(ids) > limit else None,
            )

    def get(self, token: str, target: UUID, request: UUID | None = None) -> BlindedReviewTask:
        with self.identity.transaction() as db:
            actor = self.actor(db, token)
            if not self.identity.rate(db, f"grading-audit-read:{actor}", 120, 60):
                raise IdentityError("USAGE_LIMIT_REACHED", 429)
            assignment, _, attempt, version = self.material(db, actor, target, token)
            if db.get(GradingAuditReview, assignment.id) is not None:
                raise IdentityError("REVIEW_ALREADY_COMPLETED", 409)
            document = DraftDocument.model_validate(version.document)
            if document.response_type != "SHORT_TEXT" or document.rubric is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            answer = response_projection(self.identity, attempt)["text"]
            if not isinstance(answer, str):
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            self.audit(db, actor, target, "grading_review.read", request or uuid4())
            return BlindedReviewTask(
                id=assignment.id,
                item_version_id=version.id,
                rubric_version_id=version.id,
                prompt=document.prompt,
                response=answer,
                criteria=document.rubric.criteria,
            )

    def complete(
        self, token: str, target: UUID, body: AuditReviewInput, key: UUID, request: UUID
    ) -> AuditReviewReceipt:
        points = {row.criterion_id: row.points_awarded for row in body.criterion_points}
        canonical = body.model_copy(
            update={
                "criterion_points": sorted(body.criterion_points, key=lambda row: row.criterion_id)
            }
        )
        digest = self.identity.digest("grading-review", f"{target}:{canonical.model_dump_json()}")
        with self.identity.transaction() as db:
            actor = self.actor(db, token)
            assignment, publication, _, version = self.material(db, actor, target, token)
            locked(db, publication.band_id)
            previous = db.scalar(
                select(GradingAuditReview).where(
                    GradingAuditReview.reviewer_id == actor, GradingAuditReview.request_key == key
                )
            )
            if previous is not None:
                if previous.id != target or previous.request_hash != digest:
                    raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
                self.audit(db, actor, target, "grading_review.receipt_read", request)
                return AuditReviewReceipt(id=previous.id, completed_at=previous.completed_at)
            if db.get(GradingAuditReview, assignment.id) is not None:
                raise IdentityError("REVIEW_ALREADY_COMPLETED", 409)
            if not self.identity.rate(db, f"grading-audit-write:{actor}", 30, 60):
                raise IdentityError("USAGE_LIMIT_REACHED", 429)
            rubric = DraftDocument.model_validate(version.document).rubric
            if (
                rubric is None
                or set(points) != {row.criterion_id for row in rubric.criteria}
                or any(points[row.criterion_id] > row.maximum_points for row in rubric.criteria)
            ):
                raise IdentityError("VALIDATION_FAILED", 422)
            # PostgreSQL enforces a nonfuture completion. Host/VM wall clocks can
            # differ by milliseconds; cap the domain clock at authoritative DB time
            # without relaxing the constraint or advancing injected test clocks.
            database_now = db.scalar(select(func.clock_timestamp()))
            if database_now is None:
                raise ValueError("Grading clock authority unavailable")
            now = min(self.identity.clock(), database_now)
            review = GradingAuditReview(
                id=assignment.id,
                band_id=publication.band_id,
                reviewer_id=actor,
                criterion_points=points,
                critical_error=body.critical_error,
                exact_agreement=False,
                completion_ordinal=0,
                completed_at=now,
                request_key=key,
                request_hash=digest,
                correlation_id=request,
            )
            db.add(review)
            db.flush()
            self.audit(db, actor, target, "grading_review.completed", request)
            return AuditReviewReceipt(id=review.id, completed_at=now)
