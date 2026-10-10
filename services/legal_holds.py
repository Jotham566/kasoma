"""Specific-record preservation decisions, never blanket deletion clearance."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.data_requests import DataRequestService
from services.domain.assessment import Attempt, Grade
from services.domain.data_requests import (
    DataRequest,
    DataRequestReview,
    LegalHold,
    LegalHoldReceipt,
)
from services.domain.flags import ContentFlag, FlagHistory
from services.domain.grading_work import GradingHistory
from services.domain.identity import Consent
from services.domain.mastery import MasteryEvidence, MasteryHistory
from services.identity import IdentityError, IdentityService
from services.legal_hold_contracts import HoldInput, HoldPage, HoldRelease, HoldView, RecordType
from services.staff import authorize


def active(db: Session, kind: RecordType, target: UUID, at: datetime) -> bool:
    return bool(db.scalar(select(func.record_is_held(kind, target, at))))


def active_count(db: Session, user: UUID, at: datetime) -> tuple[int, bool]:
    limited = (
        select(LegalHold.id)
        .join(DataRequest)
        .where(
            DataRequest.user_id == user,
            LegalHold.released_at.is_(None),
            LegalHold.created_at <= at,
            LegalHold.expires_at > at,
        )
        .limit(10_001)
        .subquery()
    )
    count = db.scalar(select(func.count()).select_from(limited)) or 0
    return min(count, 10_000), count > 10_000


class LegalHoldService:
    def __init__(self, identity: IdentityService):
        self.identity = identity
        self.requests = DataRequestService(identity)

    def access(self, db: Session, token: str, target: UUID) -> tuple[UUID, DataRequest]:
        actor = authorize(self.identity, db, token, {"ADMIN"}, recent=True)[0]
        request = db.scalar(select(DataRequest).where(DataRequest.id == target).with_for_update())
        if request is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if request.user_id == actor:
            raise IdentityError("SELF_REVIEW_FORBIDDEN", 403)
        if request.kind != "DELETE":
            raise IdentityError("DELETE_REQUIRED", 409)
        claim = db.get(DataRequestReview, target)
        if claim is None or claim.actor_id != actor:
            raise IdentityError("REVIEW_OWNERSHIP_REQUIRED", 403)
        if request.completed_at is not None:
            raise IdentityError("REQUEST_COMPLETED", 409)
        return actor, request

    def view(self, row: LegalHold) -> HoldView:
        return HoldView.model_validate(
            dict(
                id=row.id,
                request_id=row.request_id,
                record_type=row.record_type,
                record_id=row.record_id,
                decision_reference=row.decision_reference,
                reason=row.reason,
                status="RELEASED"
                if row.released_at
                else ("EXPIRED" if row.expires_at <= self.identity.clock() else "ACTIVE"),
                created_at=row.created_at,
                expires_at=row.expires_at,
                released_at=row.released_at,
                release_reference=row.release_reference,
            )
        )

    def replay(self, db: Session, actor: UUID, key: UUID, digest: str) -> LegalHold | None:
        receipt = db.get(LegalHoldReceipt, (actor, key))
        if receipt:
            if receipt.request_hash != digest:
                raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
            return db.get(LegalHold, receipt.hold_id)
        if not self.identity.rate(db, f"legal-hold-write:{actor}", 10, 60):
            raise IdentityError("RATE_LIMITED", 429)
        return None

    def evidence(
        self,
        db: Session,
        actor: UUID,
        row: LegalHold,
        key: UUID,
        digest: str,
        action: str,
        user: UUID,
        request_id: UUID,
    ) -> None:
        db.add(LegalHoldReceipt(actor_id=actor, key=key, request_hash=digest, hold_id=row.id))
        self.requests.audit(db, actor, row.id, action, request_id)
        self.identity.event(db, user, action, str(request_id))

    def create(
        self, token: str, target: UUID, body: HoldInput, key: UUID, request_id: UUID
    ) -> HoldView:
        # Canonicalize equivalent timezone representations for retries.
        body = body.model_copy(update={"expires_at": body.expires_at.astimezone(UTC)})
        digest = self.identity.digest("legal-hold", f"create:{target}:{body.model_dump_json()}")
        with self.identity.transaction() as db:
            actor, request = self.access(db, token, target)
            old = self.replay(db, actor, key, digest)
            if old:
                return self.view(old)
            at = self.identity.clock()
            if body.expires_at <= at:
                raise IdentityError("HOLD_END_REQUIRED", 422)
            query = {
                "CONSENT": select(Consent.id).where(
                    Consent.id == body.record_id, Consent.user_id == request.user_id
                ),
                "ATTEMPT": select(Attempt.id).where(
                    Attempt.id == body.record_id, Attempt.learner_id == request.user_id
                ),
                "GRADE": select(Grade.attempt_id)
                .join(Attempt)
                .where(Grade.attempt_id == body.record_id, Attempt.learner_id == request.user_id),
                "MASTERY_EVIDENCE": select(MasteryEvidence.id).where(
                    MasteryEvidence.id == body.record_id,
                    MasteryEvidence.learner_id == request.user_id,
                ),
                "MASTERY_HISTORY": select(MasteryHistory.id)
                .join(MasteryEvidence)
                .where(
                    MasteryHistory.id == body.record_id,
                    MasteryEvidence.learner_id == request.user_id,
                ),
                "CONTENT_FLAG": select(ContentFlag.id).where(
                    ContentFlag.id == body.record_id, ContentFlag.reporter_id == request.user_id
                ),
                "GRADING_HISTORY": select(GradingHistory.id)
                .join(Attempt, Attempt.id == GradingHistory.attempt_id)
                .where(
                    GradingHistory.id == body.record_id,
                    Attempt.learner_id == request.user_id,
                ),
                "FLAG_HISTORY": select(FlagHistory.id)
                .join(ContentFlag, ContentFlag.id == FlagHistory.flag_id)
                .where(
                    FlagHistory.id == body.record_id, ContentFlag.reporter_id == request.user_id
                ),
                "DATA_REQUEST_REVIEW": select(DataRequestReview.request_id)
                .join(DataRequest, DataRequest.id == DataRequestReview.request_id)
                .where(
                    DataRequestReview.request_id == body.record_id,
                    DataRequest.user_id == request.user_id,
                ),
                "DATA_REQUEST": select(DataRequest.id).where(
                    DataRequest.id == body.record_id, DataRequest.user_id == request.user_id
                ),
            }[body.record_type]
            if db.scalar(query.with_for_update(read=True, key_share=True)) is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            row = LegalHold(
                id=uuid4(),
                request_id=target,
                record_type=body.record_type,
                record_id=body.record_id,
                decision_reference=body.decision_reference,
                reason=body.reason,
                created_by=actor,
                created_at=at,
                expires_at=body.expires_at,
                released_at=None,
                released_by=None,
                release_reference=None,
            )
            db.add(row)
            db.flush()
            self.evidence(
                db, actor, row, key, digest, "legal_hold.created", request.user_id, request_id
            )
            return self.view(row)

    def release(
        self, token: str, target: UUID, hold: UUID, body: HoldRelease, key: UUID, request_id: UUID
    ) -> HoldView:
        digest = self.identity.digest(
            "legal-hold", f"release:{target}:{hold}:{body.model_dump_json()}"
        )
        with self.identity.transaction() as db:
            actor, request = self.access(db, token, target)
            old = self.replay(db, actor, key, digest)
            if old:
                return self.view(old)
            row = db.get(LegalHold, hold)
            if row is None or row.request_id != target:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            if row.released_at or row.expires_at <= self.identity.clock():
                raise IdentityError("HOLD_NOT_ACTIVE", 409)
            row.released_at = self.identity.clock()
            row.released_by = actor
            row.release_reference = body.decision_reference
            db.flush()
            self.evidence(
                db, actor, row, key, digest, "legal_hold.released", request.user_id, request_id
            )
            return self.view(row)

    def listing(
        self, token: str, target: UUID, cursor: UUID | None, limit: int, request_id: UUID
    ) -> HoldPage:
        with self.identity.transaction() as db:
            actor, _ = self.access(db, token, target)
            if not self.identity.rate(db, f"legal-hold-read:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            query = select(LegalHold).where(LegalHold.request_id == target)
            if cursor:
                query = query.where(LegalHold.id > cursor)
            rows = list(db.scalars(query.order_by(LegalHold.id).limit(limit + 1)))
            self.requests.audit(db, actor, target, "legal_hold.queue_read", request_id)
            return HoldPage(
                data=[self.view(r) for r in rows[:limit]],
                next_cursor=rows[limit - 1].id if len(rows) > limit else None,
            )
