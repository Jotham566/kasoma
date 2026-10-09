"""ADR-048 bounded disposable-copy cleanup; request accountability is never removed."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from time import monotonic
from typing import Protocol
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_jobs import failed, locked_job
from services.export_storage import StoredExportObject, parse_key
from services.identity import IdentityService


class CleanupStore(Protocol):
    scope: str

    def remove(self, generation: UUID, object_id: UUID) -> None: ...

    def page(
        self, *, generation: UUID | None = None, after: str | None = None, limit: int = 100
    ) -> list[StoredExportObject]: ...


@dataclass
class SweepResult:
    removed: int = 0
    generations: int = 0
    examined: int = 0
    failures: int = 0
    exhausted: bool = False
    cursor: str | None = field(default=None, repr=False)
    orphan_first: bool = False


class BudgetReached(Exception):
    pass


def prepare(identity: IdentityService, target: UUID, actor: UUID, generation_id: UUID) -> bool:
    with Session(identity.engine) as db, db.begin():
        values = locked_job(identity, db, actor, target)
        if values is None:
            return False
        request, job = values
        generation = db.get(ExportGeneration, generation_id)
        now = identity.clock()
        if (
            generation is None
            or generation.request_id != request.id
            or (generation.expires_at or generation.lease_until) > now
        ):
            return False
        if job.generation_id == generation_id:
            if job.status == "READY":
                job.status, job.updated_at, job.generation_id = "EXPIRED", now, None
            elif job.status == "RUNNING":
                failed(identity, db, request, job, "PROCESSING_FAILED")
            else:
                return False
        db.flush()
        return True


def sweep(
    identity: IdentityService,
    storage: CleanupStore,
    *,
    cursor: str | None = None,
    orphan_first: bool = False,
    timer: Callable[[], float] = monotonic,
) -> SweepResult:
    result = SweepResult(cursor=cursor, orphan_first=not orphan_first)
    finish = timer() + 10

    def phase(orphans: bool) -> None:
        deadline = min(finish, timer() + 5)
        removed, examined = 0, 0

        def checkpoint() -> None:
            if timer() >= deadline or removed >= 10 or examined >= 50:
                raise BudgetReached()

        try:
            checkpoint()
            if orphans:
                if result.cursor is not None:
                    parse_key(result.cursor, scope=storage.scope)
                page = storage.page(after=result.cursor, limit=50)
                for entry in page:
                    checkpoint()
                    # Revalidate callback output before granting any removal authority.
                    parse_key(entry.key, scope=storage.scope)
                    with Session(identity.engine) as db:
                        known = db.get(ExportGeneration, entry.generation) is not None
                    if not known and entry.modified_at + timedelta(seconds=180) <= identity.clock():
                        storage.remove(entry.generation, entry.object_id)
                        removed += 1
                        result.removed += 1
                    examined += 1
                    result.examined += 1
                    result.cursor = entry.key
                if len(page) < 50:
                    result.cursor = None
            else:
                with Session(identity.engine) as db:
                    candidates = list(
                        db.execute(
                            select(
                                ExportGeneration.id,
                                ExportGeneration.request_id,
                                DataRequest.user_id,
                            )
                            .join(DataRequest, DataRequest.id == ExportGeneration.request_id)
                            .where(
                                func.coalesce(
                                    ExportGeneration.expires_at, ExportGeneration.lease_until
                                )
                                <= identity.clock()
                            )
                            .order_by(
                                func.coalesce(
                                    ExportGeneration.expires_at, ExportGeneration.lease_until
                                ),
                                ExportGeneration.id,
                            )
                            .limit(20)
                        )
                    )
                for generation_id, target, actor in candidates:
                    checkpoint()
                    if not prepare(identity, target, actor, generation_id):
                        continue
                    # Account/DB locks are released before storage I/O.
                    limit = min(50 - examined, 10 - removed)
                    page = storage.page(generation=generation_id, limit=limit)
                    for entry in page:
                        checkpoint()
                        if entry.generation != generation_id:
                            raise ValueError("Invalid cleanup scope")
                        parse_key(entry.key, scope=storage.scope)
                        storage.remove(entry.generation, entry.object_id)
                        removed += 1
                        examined += 1
                        result.removed += 1
                        result.examined += 1
                    if len(page) < limit:
                        with Session(identity.engine) as db, db.begin():
                            generation = db.get(ExportGeneration, generation_id)
                            referenced = db.scalar(
                                select(ExportJob.request_id).where(
                                    ExportJob.generation_id == generation_id
                                )
                            )
                            if (
                                generation is not None
                                and referenced is None
                                and (generation.expires_at or generation.lease_until)
                                <= identity.clock()
                            ):
                                db.delete(generation)
                                db.flush()
                                result.generations += 1
        except BudgetReached:
            result.exhausted = True
        except Exception:
            # Keep metadata/cursor for retry; never include provider or object details in logs.
            result.failures += 1

    phase(orphan_first)
    phase(not orphan_first)
    return result
