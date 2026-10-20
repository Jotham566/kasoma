"""Specific-record preservation decisions, never blanket deletion clearance."""

from contextlib import nullcontext
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from services.account_processing import coordinate
from services.data_requests import DataRequestService
from services.domain.assessment import Attempt, Grade
from services.domain.channel_preservation import ChannelSnapshot, ChannelSnapshotBody
from services.domain.data_requests import (
    DataRequest,
    DataRequestReceipt,
    DataRequestReview,
    LegalHold,
    LegalHoldReceipt,
)
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.domain.flags import ContentFlag, FlagHistory
from services.domain.grading_audits import (
    GradingAuditAssignment,
    GradingAuditReview,
    GradingPublication,
)
from services.domain.grading_work import GradingHistory
from services.domain.identity import Consent
from services.domain.mastery import MasteryEvidence, MasteryHistory
from services.domain.messaging import InboundMessage, OutboundMessage
from services.identity import IdentityError, IdentityService
from services.legal_hold_contracts import (
    CHANNEL_RECEIPT_TYPES,
    CHANNEL_SNAPSHOT_TYPES,
    EXPORT_EVIDENCE_TYPES,
    ExportHoldSources,
    HoldInput,
    HoldPage,
    HoldRelease,
    HoldView,
    RecordType,
    supported_record_types,
)
from services.staff import authorize

WALL_CLOCK_TYPES = CHANNEL_SNAPSHOT_TYPES | EXPORT_EVIDENCE_TYPES


def active(db: Session, kind: RecordType, target: UUID, at: datetime) -> bool:
    return bool(db.scalar(select(func.record_is_held(kind, target, at))))


def database_now(db: Session) -> datetime:
    now = db.scalar(select(func.clock_timestamp()))
    if not isinstance(now, datetime):
        raise IdentityError("HOLD_TARGET_UNAVAILABLE", 503)
    return now


def active_count(db: Session, user: UUID, at: datetime) -> tuple[int, bool]:
    observed_at = case(
        (LegalHold.record_type.in_(WALL_CLOCK_TYPES), func.clock_timestamp()), else_=at
    )
    limited = (
        select(LegalHold.id)
        .join(DataRequest)
        .where(
            DataRequest.user_id == user,
            LegalHold.released_at.is_(None),
            LegalHold.created_at <= observed_at,
            LegalHold.expires_at > observed_at,
        )
        .limit(10_001)
        .subquery()
    )
    count = db.scalar(select(func.count()).select_from(limited)) or 0
    return min(count, 10_000), count > 10_000


def cleared_job_predicates() -> tuple[ColumnElement[bool], ...]:
    return (
        ExportJob.status == "EXPIRED",
        ExportJob.grant_family.is_(None),
        ExportJob.grant_authenticated_at.is_(None),
        ExportJob.generation_id.is_(None),
        ~select(ExportGeneration.id)
        .where(ExportGeneration.request_id == ExportJob.request_id)
        .exists(),
    )


class LegalHoldService:
    def __init__(self, identity: IdentityService):
        self.identity = identity
        self.requests = DataRequestService(identity)

    def access(self, db: Session, token: str, target: UUID) -> tuple[UUID, DataRequest]:
        actor = authorize(self.identity, db, token, {"ADMIN"}, recent=True)[0]
        subject = db.scalar(select(DataRequest.user_id).where(DataRequest.id == target))
        if subject is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        # Immutable ownership first; never hold a case row while waiting on closure.
        coordinate(db, subject)
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

    def view(self, row: LegalHold, at: datetime | None = None) -> HoldView:
        at = at or self.identity.clock()
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
                else ("EXPIRED" if row.expires_at <= at else "ACTIVE"),
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
            channel_receipt = body.record_type in CHANNEL_RECEIPT_TYPES
            snapshot = body.record_type in CHANNEL_SNAPSHOT_TYPES
            export_evidence = body.record_type in EXPORT_EVIDENCE_TYPES
            wall_clock = snapshot or export_evidence
            if export_evidence and not self.identity.settings.export_evidence_holds_enabled:
                raise IdentityError("HOLD_TARGET_UNAVAILABLE", 409)
            if channel_receipt and not self.identity.settings.channel_receipt_holds_enabled:
                raise IdentityError("HOLD_TARGET_UNAVAILABLE", 409)
            if snapshot and not self.identity.settings.channel_preservation_enabled:
                raise IdentityError("HOLD_TARGET_UNAVAILABLE", 409)
            if channel_receipt or snapshot:
                from services.whatsapp_linking import channel_lock

                channel_lock(self.identity, db)
            old = self.replay(db, actor, key, digest)
            if old:
                return self.view(old, database_now(db) if wall_clock else None)
            at = self.identity.clock()
            if channel_receipt or wall_clock:
                observed = database_now(db)
                at = observed if wall_clock else min(at, observed)
                review = db.get(DataRequestReview, target)
                if review is None or review.created_at > at:
                    raise IdentityError("HOLD_TARGET_UNAVAILABLE", 503)
            if body.expires_at <= at:
                raise IdentityError("HOLD_END_REQUIRED", 422)
            if body.record_type == "DATA_REQUEST_REVIEW":
                # ADR-060: lock the parent before its review, also for existing hold kinds.
                parent = db.scalar(
                    select(DataRequest.id)
                    .where(
                        DataRequest.id == body.record_id,
                        DataRequest.user_id == request.user_id,
                    )
                    .with_for_update()
                )
                if parent is None:
                    raise IdentityError("RESOURCE_NOT_FOUND", 404)
            if export_evidence:
                source_id = (
                    db.scalar(
                        select(DataRequestReceipt.request_id).where(
                            DataRequestReceipt.id == body.record_id
                        )
                    )
                    if body.record_type == "DATA_REQUEST_RECEIPT"
                    else body.record_id
                )
                source = db.scalar(
                    select(DataRequest)
                    .where(
                        DataRequest.id == source_id,
                        DataRequest.user_id == request.user_id,
                        DataRequest.kind == "EXPORT",
                    )
                    .with_for_update()
                )
                if source is None:
                    raise IdentityError("RESOURCE_NOT_FOUND", 404)
            snapshot_query = (
                select(ChannelSnapshot.id)
                .join(ChannelSnapshotBody, ChannelSnapshotBody.snapshot_id == ChannelSnapshot.id)
                .where(
                    ChannelSnapshot.id == body.record_id,
                    ChannelSnapshot.source_kind == body.record_type,
                    ChannelSnapshot.request_id == target,
                )
            )
            query = {
                "CHANNEL_LINK_SNAPSHOT": snapshot_query,
                "CHANNEL_CONVERSATION_SNAPSHOT": snapshot_query,
                "CHANNEL_INBOUND_RECEIPT": select(InboundMessage.id).where(
                    InboundMessage.id == body.record_id,
                    InboundMessage.actor_id == request.user_id,
                    InboundMessage.status != "QUEUED",
                    InboundMessage.processed_at.is_not(None),
                    InboundMessage.sender_encrypted.is_(None),
                    InboundMessage.code_hash.is_(None),
                    InboundMessage.reply_encrypted.is_(None),
                ),
                "CHANNEL_OUTBOUND_RECEIPT": select(OutboundMessage.id).where(
                    OutboundMessage.id == body.record_id,
                    OutboundMessage.actor_id == request.user_id,
                    OutboundMessage.status != "PENDING",
                    OutboundMessage.recipient_encrypted.is_(None),
                ),
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
                "GRADING_PUBLICATION": select(GradingPublication.attempt_id)
                .join(Attempt, Attempt.id == GradingPublication.attempt_id)
                .where(
                    GradingPublication.attempt_id == body.record_id,
                    Attempt.learner_id == request.user_id,
                ),
                "GRADING_AUDIT": select(GradingAuditAssignment.id)
                .join(Attempt, Attempt.id == GradingAuditAssignment.attempt_id)
                .where(
                    GradingAuditAssignment.id == body.record_id,
                    Attempt.learner_id == request.user_id,
                ),
                "GRADING_REVIEW": select(GradingAuditReview.id)
                .join(GradingAuditAssignment, GradingAuditAssignment.id == GradingAuditReview.id)
                .join(Attempt, Attempt.id == GradingAuditAssignment.attempt_id)
                .where(
                    GradingAuditReview.id == body.record_id,
                    Attempt.learner_id == request.user_id,
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
                "DATA_REQUEST_RECEIPT": select(DataRequestReceipt.id).where(
                    DataRequestReceipt.id == body.record_id,
                ),
                "EXPORT_JOB_RECEIPT": select(ExportJob.request_id).where(
                    ExportJob.request_id == body.record_id,
                    *cleared_job_predicates(),
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
            locked = (
                query.with_for_update(of=ChannelSnapshotBody)
                if snapshot
                else (
                    query.with_for_update()
                    if export_evidence
                    else query.with_for_update(read=True, key_share=True)
                )
            )
            if db.scalar(locked) is None:
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
            with db.begin_nested() if snapshot else nullcontext():
                db.add(row)
                db.flush()
                self.evidence(
                    db, actor, row, key, digest, "legal_hold.created", request.user_id, request_id
                )
            return self.view(row, at if wall_clock else None)

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
                return self.view(
                    old, database_now(db) if old.record_type in WALL_CLOCK_TYPES else None
                )
            row = db.get(LegalHold, hold)
            if row is None or row.request_id != target:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            snapshot = row.record_type in WALL_CLOCK_TYPES
            at = database_now(db) if snapshot else self.identity.clock()
            if row.released_at or row.expires_at <= at:
                raise IdentityError("HOLD_NOT_ACTIVE", 409)
            with db.begin_nested() if snapshot else nullcontext():
                row.released_at = at
                row.released_by = actor
                row.release_reference = body.decision_reference
                db.flush()
                self.evidence(
                    db, actor, row, key, digest, "legal_hold.released", request.user_id, request_id
                )
            return self.view(row, at if snapshot else None)

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
            observed = (
                database_now(db)
                if any(row.record_type in WALL_CLOCK_TYPES for row in rows[:limit])
                else None
            )
            self.requests.audit(db, actor, target, "legal_hold.queue_read", request_id)
            return HoldPage(
                data=[
                    self.view(r, observed if r.record_type in WALL_CLOCK_TYPES else None)
                    for r in rows[:limit]
                ],
                next_cursor=rows[limit - 1].id if len(rows) > limit else None,
                supported_record_types=supported_record_types(
                    self.identity.settings.channel_receipt_holds_enabled,
                    self.identity.settings.channel_preservation_enabled,
                    self.identity.settings.export_evidence_holds_enabled,
                ),
            )

    def export_sources(
        self,
        token: str,
        target: UUID,
        source: UUID,
        cursor: UUID | None,
        limit: int,
        request_id: UUID,
    ) -> ExportHoldSources:
        with self.identity.transaction() as db:
            actor, case = self.access(db, token, target)
            if not self.identity.rate(db, f"legal-hold-read:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            parent = db.scalar(
                select(DataRequest)
                .where(
                    DataRequest.id == source,
                    DataRequest.user_id == case.user_id,
                    DataRequest.kind == "EXPORT",
                )
                .with_for_update()
            )
            if parent is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            query = select(DataRequestReceipt.id).where(
                DataRequestReceipt.request_id == source,
            )
            if cursor is not None:
                query = query.where(DataRequestReceipt.id > cursor)
            receipts = list(db.scalars(query.order_by(DataRequestReceipt.id).limit(limit + 1)))
            job = db.scalar(
                select(ExportJob.request_id).where(
                    ExportJob.request_id == source,
                    *cleared_job_predicates(),
                )
            )
            self.requests.audit(db, actor, target, "legal_hold.export_sources_read", request_id)
            return ExportHoldSources(
                receipt_ids=receipts[:limit],
                next_cursor=receipts[limit - 1] if len(receipts) > limit else None,
                export_job_id=job,
            )
