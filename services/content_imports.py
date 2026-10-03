"""Bounded asynchronous draft import with durable PostgreSQL retry truth."""

from datetime import timedelta
from uuid import UUID, uuid4, uuid5

from sqlalchemy import String, literal, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from services.content import ContentError, ContentService, digest
from services.domain.content import AuditLog, ContentImport, Item, ItemVersion
from services.domain.identity import User, UserRole
from services.identity import IdentityService
from services.import_contracts import ImportInput, ImportPage, ImportResult, ImportView
from services.observability import emit
from services.staff import authorize


def view(row: ContentImport) -> ImportView:
    return ImportView(
        id=row.id,
        status=row.status,
        created_at=row.created_at,
        finished_at=row.finished_at,
        attempts=row.attempts,
        error_code=row.error_code,
        results=[ImportResult.model_validate(r) for r in row.results],
    )


def audit(identity: IdentityService, db: Session, row: ContentImport, action: str) -> None:
    db.add(
        AuditLog(
            id=uuid4(),
            actor_id=row.actor_id,
            target_id=row.id,
            action=action,
            reason="Synthetic draft import workflow",
            request_id=row.request_id,
            before_hash=None,
            after_hash=row.request_hash,
            created_at=identity.clock(),
        )
    )


class ImportService:
    def __init__(self, identity: IdentityService):
        self.identity = identity
        self.content = ContentService(identity)

    def enqueue(self, token: str, body: ImportInput, key: UUID, request_id: UUID) -> ImportView:
        fingerprint = digest(body.model_dump(mode="json"))
        with self.identity.transaction() as db:
            actor = authorize(self.identity, db, token, {"CONTENT_AUTHOR"}, recent=True)[0]
            old = db.scalar(
                select(ContentImport).where(
                    ContentImport.actor_id == actor, ContentImport.key == key
                )
            )
            if old:
                if old.request_hash != fingerprint:
                    raise ContentError("IDEMPOTENCY_CONFLICT")
                return view(old)
            if not self.identity.rate(db, f"content-import-write:{actor}", 5, 3600):
                raise ContentError("RATE_LIMITED", status=429)
            for index, record in enumerate(body.records):
                try:
                    self.content.validate(db, record.subject_id, record.document, complete=False)
                    if not record.change_reason.strip():
                        raise ContentError("CONTENT_VALIDATION_FAILED", ["change_reason"])
                except ContentError as exc:
                    raise ContentError(
                        "CONTENT_VALIDATION_FAILED",
                        [f"records.{index}.{field}" for field in exc.fields],
                        422,
                    ) from None
            now = self.identity.clock()
            row = ContentImport(
                id=uuid4(),
                actor_id=actor,
                key=key,
                request_hash=fingerprint,
                request_id=request_id,
                payload=body.model_dump(mode="json"),
                results=[],
                status="QUEUED",
                attempts=0,
                error_code=None,
                created_at=now,
                available_at=now,
                expires_at=now + timedelta(hours=24),
                finished_at=None,
            )
            db.add(row)
            db.flush()
            audit(self.identity, db, row, "content_import.queued")
            return view(row)

    def listing(
        self, token: str, target: UUID | None, cursor: UUID | None = None, limit: int = 20
    ) -> ImportPage:
        with self.identity.transaction() as db:
            actor = authorize(self.identity, db, token, {"CONTENT_AUTHOR"})[0]
            if not self.identity.rate(db, f"content-import-read:{actor}", 60, 60):
                raise ContentError("RATE_LIMITED", status=429)
            query = select(ContentImport).where(ContentImport.actor_id == actor)
            if target:
                row = db.scalar(query.where(ContentImport.id == target))
                if row is None:
                    raise ContentError("RESOURCE_NOT_FOUND", status=404)
                return ImportPage(data=[view(row)], next_cursor=None)
            if cursor:
                query = query.where(ContentImport.id > cursor)
            rows = list(db.scalars(query.order_by(ContentImport.id).limit(limit + 1)))
            return ImportPage(
                data=[view(row) for row in rows[:limit]],
                next_cursor=rows[limit - 1].id if len(rows) > limit else None,
            )


def process_one(identity: IdentityService) -> bool:
    """Rollback all candidate changes before recording a retry; never store exception text."""
    with Session(identity.engine) as db, db.begin():
        now = identity.clock()
        row = db.scalar(
            select(ContentImport)
            .where(ContentImport.status == "QUEUED", ContentImport.available_at <= now)
            .order_by(ContentImport.created_at, ContentImport.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if row is None:
            return False
        identity.lock(db, str(row.actor_id))
        user = db.get(User, row.actor_id)
        active_author = (
            user is not None
            and user.status == "ACTIVE"
            and db.get(UserRole, (row.actor_id, "CONTENT_AUTHOR")) is not None
        )
        code = (
            "IMPORT_EXPIRED"
            if row.expires_at <= now
            else (None if active_author else "AUTHOR_UNAVAILABLE")
        )
        results = []
        permanent = code is not None
        if code is None:
            try:
                with db.begin_nested():
                    body = ImportInput.model_validate(row.payload)
                    content = ContentService(identity)
                    for index, record in enumerate(body.records):
                        document = record.document.model_dump(
                            mode="json", exclude={"source_locator"}
                        )
                        duplicate = db.scalar(
                            select(ItemVersion)
                            .join(Item)
                            .where(
                                Item.author_id == row.actor_id,
                                Item.subject_id == record.subject_id,
                                ItemVersion.document.cast(JSONB).op("-")(
                                    literal("source_locator", type_=String)
                                )
                                == document,
                            )
                            .order_by(ItemVersion.created_at, ItemVersion.id)
                            .limit(1)
                        )
                        if duplicate:
                            version_id, outcome = duplicate.id, "DUPLICATE"
                        else:
                            created = content.create_in_transaction(
                                db,
                                row.actor_id,
                                {"CONTENT_AUTHOR"},
                                record.draft(),
                                uuid5(row.id, str(index)),
                                row.request_id,
                            )
                            version_id, outcome = created.id, "CREATED"
                        results.append(
                            ImportResult(
                                position=index + 1, version_id=version_id, outcome=outcome
                            ).model_dump(mode="json")
                        )
            except ContentError:
                code, permanent = "CANDIDATE_INVALID", True
            except Exception:
                code = "TRANSIENT_FAILURE"
        row.attempts += 1
        row.error_code = code
        if code is None:
            row.status, row.results = "COMPLETED", results
        elif permanent or row.attempts >= 3:
            row.status = "FAILED"
        else:
            row.available_at = now + timedelta(seconds=60 * row.attempts)
        if row.status != "QUEUED":
            row.payload, row.finished_at = None, now
        audit(identity, db, row, "content_import." + row.status.lower())
        db.flush()
        event, correlation = "content_import." + row.status.lower(), str(row.request_id)
    emit(event, correlation, "WORKER", 200 if code is None else 503)
    return True


def process_imports(identity: IdentityService) -> int:
    return sum(1 for _ in range(5) if process_one(identity))
