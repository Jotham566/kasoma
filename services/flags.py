"""Owned flag reporting and independently authorized, atomic staff triage."""

import calendar
import json
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.account_processing import coordinate
from services.assessment import AssessmentService
from services.domain.assessment import AssessmentSession, Attempt, SessionItem
from services.domain.content import AuditLog, ContentEvent, Item, ItemVersion
from services.domain.flags import ContentFlag, FlagHistory, FlagMutationReceipt
from services.flag_contracts import (
    FlagDetail,
    FlagHistoryView,
    FlagInput,
    FlagPage,
    FlagReceipt,
    FlagSummary,
    FlagUpdate,
    Status,
)
from services.identity import IdentityError, IdentityService
from services.staff import authorize

STAFF = {"ACADEMIC_REVIEWER", "ADMIN"}


def retention_due(at: datetime) -> datetime:
    year = at.year + 2
    return at.replace(year=year, day=min(at.day, calendar.monthrange(year, at.month)[1]))


class FlagService:
    def __init__(self, identity: IdentityService):
        self.identity = identity

    def fingerprint(self, value: object) -> str:
        return self.identity.digest("flag-payload", json.dumps(value, sort_keys=True))

    def owned(self, db: Session, token: str, attempt_id: UUID) -> tuple[UUID, Attempt]:
        assessment = AssessmentService(self.identity)
        actor = assessment.authorize(db, token)
        attempt = db.get(Attempt, attempt_id)
        if attempt is None or attempt.learner_id != actor:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        session = db.scalar(
            select(AssessmentSession)
            .join(SessionItem)
            .where(SessionItem.id == attempt.session_item_id)
        )
        if session is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        assessment.authorize(db, token, session.subject_id)
        return actor, attempt

    def summary(self, row: ContentFlag) -> FlagSummary:
        return FlagSummary.model_validate(
            {key: getattr(row, key) for key in FlagSummary.model_fields}
        )

    def detail(self, db: Session, row: ContentFlag) -> FlagDetail:
        return FlagDetail(
            **self.summary(row).model_dump(),
            comment=self.identity.decrypt(row.comment_encrypted),
            resolution=self.identity.decrypt(row.resolution_encrypted)
            if row.resolution_encrypted
            else "",
            resolved_at=row.resolved_at,
            retention_due_at=row.retention_due_at,
            history=[
                FlagHistoryView.model_validate(
                    {key: getattr(h, key) for key in FlagHistoryView.model_fields}
                )
                for h in db.scalars(
                    select(FlagHistory)
                    .where(FlagHistory.flag_id == row.id)
                    .order_by(FlagHistory.revision)
                )
            ],
        )

    def receipt(self, row: ContentFlag) -> FlagReceipt:
        return FlagReceipt.model_validate(
            dict(id=row.id, category=row.category, created_at=row.created_at)
        )

    def replay(self, db: Session, actor: UUID, key: UUID, fingerprint: str) -> ContentFlag | None:
        receipt = db.get(FlagMutationReceipt, (actor, key))
        if receipt is None:
            return None
        if receipt.request_hash != fingerprint:
            raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
        return db.get(ContentFlag, receipt.flag_id)

    def audit(
        self,
        db: Session,
        actor: UUID,
        target: UUID,
        action: str,
        request_id: UUID,
        before: str | None = None,
        after: str | None = None,
    ) -> None:
        db.add(
            AuditLog(
                id=uuid4(),
                actor_id=actor,
                target_id=target,
                action=action,
                reason="Flag workflow metadata only",
                request_id=request_id,
                before_hash=before,
                after_hash=after,
                created_at=self.identity.clock(),
            )
        )

    def record(
        self, db: Session, actor: UUID, row: ContentFlag, request_id: UUID, before: str | None
    ) -> None:
        db.flush()
        db.add(
            FlagHistory(
                id=uuid4(),
                flag_id=row.id,
                actor_id=actor,
                revision=row.revision,
                status=row.status,
                priority=row.priority,
                owner_id=row.owner_id,
                resolution_hash=self.identity.digest("flag-resolution", row.resolution_encrypted)
                if row.resolution_encrypted
                else None,
                created_at=row.updated_at,
            )
        )
        action = "content.flag.created" if row.revision == 1 else "content.flag.updated"
        self.audit(
            db,
            actor,
            row.id,
            action,
            request_id,
            before,
            self.fingerprint(self.summary(row).model_dump(mode="json")),
        )
        db.add(
            ContentEvent(
                id=uuid4(),
                item_version_id=row.item_version_id,
                type=action,
                version=1,
                request_id=request_id,
                created_at=self.identity.clock(),
            )
        )
        db.flush()

    def create(
        self, token: str, attempt_id: UUID, body: FlagInput, key: UUID, request_id: UUID
    ) -> FlagReceipt:
        with Session(self.identity.engine) as db, db.begin():
            actor, attempt = self.owned(db, token, attempt_id)
            fingerprint = self.fingerprint(
                {"action": "report", "attempt": str(attempt_id), "body": body.model_dump()}
            )
            replay = self.replay(db, actor, key, fingerprint)
            if replay:
                return self.receipt(replay)
            existing = db.scalar(
                select(ContentFlag).where(
                    ContentFlag.attempt_id == attempt_id, ContentFlag.category == body.category
                )
            )
            if existing:
                if existing.report_hash != fingerprint:
                    raise IdentityError("FLAG_ALREADY_REPORTED", 409)
                row = existing
            else:
                if not self.identity.rate(db, "flag-create:" + str(actor), 10, 3600):
                    raise IdentityError("USAGE_LIMIT_REACHED", 429)
                version = db.get(ItemVersion, attempt.item_version_id)
                if version is None:
                    raise IdentityError("RESOURCE_NOT_FOUND", 404)
                db.scalar(select(Item).where(Item.id == version.item_id).with_for_update())
                now = self.identity.clock()
                row = ContentFlag(
                    id=uuid4(),
                    item_id=version.item_id,
                    item_version_id=version.id,
                    attempt_id=attempt.id,
                    reporter_id=actor,
                    category=body.category,
                    comment_encrypted=self.identity.encrypt(body.comment),
                    report_hash=fingerprint,
                    status="OPEN",
                    priority="HIGH" if body.category == "UNSAFE_CONTENT" else "NORMAL",
                    owner_id=None,
                    revision=1,
                    resolution_encrypted=None,
                    created_at=now,
                    updated_at=now,
                    resolved_at=None,
                    retention_due_at=None,
                )
                db.add(row)
                self.record(db, actor, row, request_id, None)
            db.add(
                FlagMutationReceipt(
                    actor_id=actor, key=key, request_hash=fingerprint, flag_id=row.id
                )
            )
            return self.receipt(row)

    def owned_reports(self, token: str, attempt_id: UUID) -> list[FlagReceipt]:
        with Session(self.identity.engine) as db, db.begin():
            actor, _ = self.owned(db, token, attempt_id)
            self.limit(db, actor)
            return [
                self.receipt(row)
                for row in db.scalars(
                    select(ContentFlag)
                    .where(ContentFlag.attempt_id == attempt_id)
                    .order_by(ContentFlag.created_at, ContentFlag.id)
                )
            ]

    def limit(self, db: Session, actor: UUID) -> None:
        if not self.identity.rate(db, "flag-access:" + str(actor), 60, 60):
            raise IdentityError("USAGE_LIMIT_REACHED", 429)

    def list(
        self, token: str, cursor: UUID | None, limit: int, status: Status | None, request_id: UUID
    ) -> FlagPage:
        with Session(self.identity.engine) as db, db.begin():
            actor, _ = authorize(self.identity, db, token, STAFF)
            self.limit(db, actor)
            query = select(ContentFlag).order_by(ContentFlag.id).limit(limit + 1)
            if cursor:
                query = query.where(ContentFlag.id > cursor)
            if status:
                query = query.where(ContentFlag.status == status)
            rows = list(db.scalars(query))
            self.audit(db, actor, actor, "content.flag.queue_read", request_id)
            return FlagPage(
                data=[self.summary(r) for r in rows[:limit]],
                next_cursor=rows[limit - 1].id if len(rows) > limit else None,
            )

    def get(self, token: str, flag_id: UUID, request_id: UUID) -> FlagDetail:
        with Session(self.identity.engine) as db, db.begin():
            actor, _ = authorize(self.identity, db, token, STAFF)
            self.limit(db, actor)
            subject = db.scalar(select(ContentFlag.reporter_id).where(ContentFlag.id == flag_id))
            if subject is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            coordinate(db, subject)
            row = db.get(ContentFlag, flag_id)
            if row is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            self.audit(db, actor, row.id, "content.flag.read", request_id)
            return self.detail(db, row)

    def update(
        self, token: str, flag_id: UUID, body: FlagUpdate, key: UUID, request_id: UUID
    ) -> FlagDetail:
        with Session(self.identity.engine) as db, db.begin():
            actor, _ = authorize(self.identity, db, token, STAFF, recent=True)
            self.limit(db, actor)
            subject = db.scalar(select(ContentFlag.reporter_id).where(ContentFlag.id == flag_id))
            if subject is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            coordinate(db, subject)
            fingerprint = self.fingerprint(
                {"action": "triage", "flag": str(flag_id), "body": body.model_dump()}
            )
            replay = self.replay(db, actor, key, fingerprint)
            if replay:
                self.audit(db, actor, replay.id, "content.flag.read", request_id)
                return self.detail(db, replay)
            row = db.scalar(select(ContentFlag).where(ContentFlag.id == flag_id).with_for_update())
            if row is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            version = db.get(ItemVersion, row.item_version_id)
            if version is None or version.author_id == actor:
                raise IdentityError("SELF_REVIEW_FORBIDDEN", 409)
            if row.revision != body.expected_revision:
                raise IdentityError("VERSION_CONFLICT", 409)
            if not body.claim and row.owner_id != actor:
                raise IdentityError("FLAG_CLAIM_REQUIRED", 409)
            before = self.fingerprint(self.summary(row).model_dump(mode="json"))
            row.owner_id = actor
            row.status, row.priority = body.status, body.priority
            row.revision += 1
            row.updated_at = self.identity.clock()
            row.resolution_encrypted = (
                self.identity.encrypt(body.resolution) if body.resolution else None
            )
            row.resolved_at = row.updated_at if body.status in {"RESOLVED", "DISMISSED"} else None
            row.retention_due_at = retention_due(row.resolved_at) if row.resolved_at else None
            self.record(db, actor, row, request_id, before)
            db.add(
                FlagMutationReceipt(
                    actor_id=actor, key=key, request_hash=fingerprint, flag_id=row.id
                )
            )
            return self.detail(db, row)
