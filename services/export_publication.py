"""ADR-048 in progress: fresh authorization before snapshot and atomic publication."""

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from datetime import timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from services.data_exports import retention_due
from services.data_requests import DataRequestService
from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_artifacts import parse_manifest
from services.export_job_contracts import ExportFailure
from services.export_jobs import ExportClaim, grant_valid, locked_job
from services.identity import IdentityService


class ExportStopped(RuntimeError):
    def __init__(self, reason: ExportFailure = "PROCESSING_FAILED") -> None:
        self.reason = reason
        super().__init__(reason)


def validate_claim(
    identity: IdentityService, db: Session, claim: ExportClaim
) -> tuple[DataRequest, ExportJob, ExportGeneration]:
    request = db.get(DataRequest, claim.request_id)
    job = db.get(ExportJob, claim.request_id)
    generation = db.get(ExportGeneration, claim.generation_id)
    if (
        request is None
        or request.user_id != claim.actor_id
        or job is None
        or generation is None
        or generation.request_id != request.id
        or job.status != "RUNNING"
        or job.generation_id != claim.generation_id
        or generation.published_at is not None
        or generation.lease_until <= identity.clock()
    ):
        raise ExportStopped()
    if request.completed_at is not None:
        raise ExportStopped("REQUEST_COMPLETED")
    if (
        job.grant_family != claim.family
        or job.grant_authenticated_at != claim.authenticated_at
        or not grant_valid(identity, db, job)
    ):
        raise ExportStopped("AUTH_REQUIRED")
    return request, job, generation


@contextmanager
def snapshot(identity: IdentityService, claim: ExportClaim) -> Iterator[Session]:
    # The separate snapshot must not exist before authorization's account lock is acquired.
    with ExitStack() as stack:
        coordinator = stack.enter_context(Session(identity.engine))
        coordination = stack.enter_context(coordinator.begin())
        if locked_job(identity, coordinator, claim.actor_id, claim.request_id) is None:
            raise ExportStopped()
        validate_claim(identity, coordinator, claim)
        connection = stack.enter_context(
            identity.engine.connect().execution_options(isolation_level="REPEATABLE READ")
        )
        reader = stack.enter_context(Session(bind=connection))
        stack.enter_context(reader.begin())
        reader.execute(text("SET TRANSACTION READ ONLY"))
        validate_claim(identity, reader, claim)  # Establish the snapshot while the lock is held.
        coordination.commit()
        coordinator.close()
        yield reader


def publish(identity: IdentityService, claim: ExportClaim, raw_manifest: bytes) -> None:
    manifest = parse_manifest(raw_manifest, claim.request_id, claim.generation_id)
    requests = DataRequestService(identity)
    with Session(identity.engine) as db, db.begin():
        if locked_job(identity, db, claim.actor_id, claim.request_id) is None:
            raise ExportStopped()
        request, job, generation = validate_claim(identity, db, claim)
        now = identity.clock()
        generation.published_at, generation.expires_at = now, now + timedelta(hours=24)
        generation.encrypted_manifest = identity.encrypt(raw_manifest.decode("utf-8"))
        generation.digest, generation.size = manifest.digest, manifest.size
        db.flush()
        request.completed_at = now
        request.retention_due_at, request.export_digest = retention_due(now), manifest.digest
        db.flush()
        job.status, job.updated_at, job.finished_at = "READY", now, now
        job.grant_family, job.grant_authenticated_at = None, None
        job.failure, job.next_attempt_at = None, None
        db.flush()
        requests.audit(
            db, claim.actor_id, claim.request_id, "data_export.completed", claim.correlation_id
        )
        identity.event(db, claim.actor_id, "data_export.completed", str(claim.correlation_id))
