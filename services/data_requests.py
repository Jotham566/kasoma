"""FR-ID-006 request intake, acknowledgement and independent admin review.

Learning consent is not required to exercise privacy rights. Export fulfillment is
owned by data_exports; deletion processing and external communication remain gated.
"""

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.data_request_contracts import DataRequestInput, DataRequestPage, DataRequestView
from services.domain.content import AuditLog
from services.domain.data_requests import DataRequest, DataRequestReceipt, DataRequestReview
from services.identity import IdentityError, IdentityService
from services.staff import authorize


class DataRequestService:
    def __init__(self, identity: IdentityService):
        self.identity = identity

    def view(self, db: Session, row: DataRequest) -> DataRequestView:
        review = db.get(DataRequestReview, row.id)
        return DataRequestView.model_validate(
            dict(
                id=row.id,
                kind=row.kind,
                created_at=row.created_at,
                status="COMPLETED" if row.completed_at else ("IN_REVIEW" if review else "QUEUED"),
                completed_at=row.completed_at,
                retention_due_at=row.retention_due_at,
                download_expires_at=row.completed_at + timedelta(hours=24)
                if row.completed_at
                else None,
                reviewed_at=review.created_at if review else None,
                retention_policy=row.retention_policy,
            )
        )

    def audit(self, db: Session, actor: UUID, target: UUID, action: str, request_id: UUID) -> None:
        db.add(
            AuditLog(
                id=uuid4(),
                actor_id=actor,
                target_id=target,
                action=action,
                reason="Minimized data-request workflow metadata",
                request_id=request_id,
                before_hash=None,
                after_hash=None,
                created_at=self.identity.clock(),
            )
        )

    def replay(self, db: Session, actor: UUID, key: UUID, fingerprint: str) -> DataRequest | None:
        receipt = db.get(DataRequestReceipt, (actor, key))
        if receipt is None:
            return None
        if receipt.request_hash != fingerprint:
            raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
        return db.get(DataRequest, receipt.request_id)

    def receipt(
        self, db: Session, actor: UUID, key: UUID, fingerprint: str, row: DataRequest
    ) -> None:
        db.add(
            DataRequestReceipt(actor_id=actor, key=key, request_hash=fingerprint, request_id=row.id)
        )

    def create(
        self, token: str, body: DataRequestInput, key: UUID, request_id: UUID
    ) -> DataRequestView:
        with self.identity.transaction() as db:
            auth = self.identity.authenticate(db, token, recent=True)
            actor = auth.user_id
            fingerprint = self.identity.digest("data-request", "create:" + body.kind)
            old = self.replay(db, actor, key, fingerprint)
            if old:
                return self.view(db, old)
            # Bound distinct keys too. Reads/retries are not blocked by learning withdrawal.
            if not self.identity.rate(db, f"data-request-create:{actor}", 10, 3600):
                raise IdentityError("RATE_LIMITED", 429)
            row = db.scalar(
                select(DataRequest).where(
                    DataRequest.user_id == actor,
                    DataRequest.kind == body.kind,
                    DataRequest.completed_at.is_(None),
                )
            )
            if row is None:
                row = DataRequest(
                    id=uuid4(),
                    user_id=actor,
                    kind=body.kind,
                    authenticated_at=auth.authenticated_at,
                    verification_method="RECENT_OTP",
                    retention_policy="SIX_YEARS_AFTER_COMPLETION",
                    created_at=self.identity.clock(),
                )
                db.add(row)
                db.flush()
                self.audit(db, actor, row.id, "data_request.created", request_id)
                self.identity.event(db, actor, "data_request.created", str(request_id))
            self.receipt(db, actor, key, fingerprint, row)
            return self.view(db, row)

    def listing(
        self, token: str, cursor: UUID | None, limit: int, request_id: UUID, staff: bool = False
    ) -> DataRequestPage:
        with self.identity.transaction() as db:
            actor = (
                authorize(self.identity, db, token, {"ADMIN"}, recent=True)[0]
                if staff
                else (self.identity.authenticate(db, token).user_id)
            )
            if not self.identity.rate(db, f"data-request-read:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            query = select(DataRequest)
            if not staff:
                query = query.where(DataRequest.user_id == actor)
            if cursor:
                query = query.where(DataRequest.id > cursor)
            rows = list(db.scalars(query.order_by(DataRequest.id).limit(limit + 1)))
            if staff:
                self.audit(db, actor, actor, "data_request.queue_read", request_id)
            return DataRequestPage(
                data=[self.view(db, r) for r in rows[:limit]],
                next_cursor=rows[limit - 1].id if len(rows) > limit else None,
            )

    def get(self, token: str, target: UUID) -> DataRequestView:
        with self.identity.transaction() as db:
            actor = self.identity.authenticate(db, token).user_id
            if not self.identity.rate(db, f"data-request-read:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            row = db.get(DataRequest, target)
            if row is None or row.user_id != actor:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            return self.view(db, row)

    def claim(self, token: str, target: UUID, key: UUID, request_id: UUID) -> DataRequestView:
        with self.identity.transaction() as db:
            actor = authorize(self.identity, db, token, {"ADMIN"}, recent=True)[0]
            fingerprint = self.identity.digest("data-request", "claim:" + str(target))
            old = self.replay(db, actor, key, fingerprint)
            if old:
                return self.view(db, old)
            if not self.identity.rate(db, f"data-request-claim:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            row = db.scalar(select(DataRequest).where(DataRequest.id == target).with_for_update())
            if row is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            if row.completed_at:
                raise IdentityError("REQUEST_COMPLETED", 409)
            if row.user_id == actor:
                raise IdentityError("SELF_REVIEW_FORBIDDEN", 403)
            review = db.get(DataRequestReview, target)
            if review and review.actor_id != actor:
                raise IdentityError("ALREADY_CLAIMED", 409)
            if review is None:
                db.add(
                    DataRequestReview(
                        request_id=target, actor_id=actor, created_at=self.identity.clock()
                    )
                )
                self.audit(db, actor, target, "data_request.review_started", request_id)
                self.identity.event(db, row.user_id, "data_request.review_started", str(request_id))
                db.flush()
            self.receipt(db, actor, key, fingerprint, row)
            return self.view(db, row)
