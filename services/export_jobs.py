"""ADR-048 work in progress: owner commands and serialized background claims."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from services.data_requests import DataRequestService
from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_job_contracts import ExportFailure, ExportJobView
from services.identity import IdentityError, IdentityService


@dataclass(frozen=True)
class ExportClaim:
    request_id: UUID
    actor_id: UUID
    generation_id: UUID
    family: UUID
    authenticated_at: datetime
    correlation_id: UUID


def grant_valid(identity: IdentityService, db: Session, job: ExportJob) -> bool:
    return bool(
        db.scalar(
            func.export_grant_valid(
                job.request_id, job.grant_family, job.grant_authenticated_at, identity.clock()
            )
        )
    )


def job_view(identity: IdentityService, db: Session, job: ExportJob) -> ExportJobView:
    generation = db.get(ExportGeneration, job.generation_id) if job.generation_id else None
    expired = generation and generation.expires_at and generation.expires_at <= identity.clock()
    return ExportJobView.model_validate(
        dict(
            request_id=job.request_id,
            status="EXPIRED" if expired else job.status,
            queued_at=job.queued_at,
            finished_at=job.finished_at,
            attempts=job.attempts,
            failure=job.failure,
            expires_at=generation.expires_at if generation else None,
            size_bytes=generation.size if generation else None,
        )
    )


def queue(
    identity: IdentityService, token: str, target: UUID, key: UUID, correlation_id: UUID
) -> ExportJobView:
    requests = DataRequestService(identity)
    with identity.transaction() as db:
        auth = identity.authenticate(db, token, recent=True)
        request = db.scalar(
            select(DataRequest)
            .where(DataRequest.id == target, DataRequest.user_id == auth.user_id)
            .with_for_update()
        )
        if request is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if request.kind != "EXPORT":
            raise IdentityError("EXPORT_REQUIRED", 409)
        fingerprint = identity.digest("data-request", "queue-export:" + str(target))
        replay = requests.replay(db, auth.user_id, key, fingerprint)
        job = db.get(ExportJob, target)
        if replay is not None and job is not None:
            return job_view(identity, db, job)
        if request.completed_at is not None:
            raise IdentityError("REQUEST_COMPLETED", 409)
        if not identity.rate(db, f"export-job-command:{auth.user_id}", 3, 3600):
            raise IdentityError("RATE_LIMITED", 429)
        now = identity.clock()
        if job is None:
            job = ExportJob(request_id=target, created_at=now)
            db.add(job)
        if job.status is None or job.status == "FAILED":
            job.status, job.attempts, job.failure = "QUEUED", 0, None
            job.correlation_id = correlation_id
            job.queued_at = job.updated_at = job.next_attempt_at = now
            job.finished_at, job.generation_id = None, None
            job.grant_family, job.grant_authenticated_at = auth.family, auth.authenticated_at
            db.flush()
            requests.audit(db, auth.user_id, target, "data_export.queued", correlation_id)
            identity.event(db, auth.user_id, "data_export.queued", str(correlation_id))
        requests.receipt(db, auth.user_id, key, fingerprint, request)
        return job_view(identity, db, job)


def status(identity: IdentityService, token: str, target: UUID) -> ExportJobView:
    with identity.transaction() as db:
        actor = identity.authenticate(db, token, recent=True).user_id
        if not identity.rate(db, f"export-job-status:{actor}", 60, 60):
            raise IdentityError("RATE_LIMITED", 429)
        request = db.get(DataRequest, target)
        if request is None or request.user_id != actor:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        job = db.get(ExportJob, target)
        if job is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        return job_view(identity, db, job)


def locked_job(
    identity: IdentityService, db: Session, actor: UUID, target: UUID
) -> tuple[DataRequest, ExportJob] | None:
    identity.lock(db, str(actor))
    request = db.scalar(
        select(DataRequest)
        .where(DataRequest.id == target, DataRequest.user_id == actor)
        .with_for_update()
    )
    job = db.scalar(select(ExportJob).where(ExportJob.request_id == target).with_for_update())
    return (request, job) if request is not None and job is not None else None


def failed(
    identity: IdentityService,
    db: Session,
    request: DataRequest,
    job: ExportJob,
    reason: ExportFailure,
) -> None:
    now = identity.clock()
    if request.completed_at:
        reason = "REQUEST_COMPLETED"
    elif not grant_valid(identity, db, job):
        reason = "AUTH_REQUIRED"
    retry = reason == "PROCESSING_FAILED" and 0 < job.attempts < 3
    job.status = "QUEUED" if retry else "FAILED"
    job.updated_at, job.failure, job.generation_id = now, reason, None
    job.next_attempt_at = now + timedelta(seconds=30 * 2 ** (job.attempts - 1)) if retry else None
    job.finished_at = None if retry else now
    if not retry:
        job.grant_family, job.grant_authenticated_at = None, None
    db.flush()


def claim_next(identity: IdentityService) -> ExportClaim | None:
    # Lookup is unlocked; authoritative reads happen after the account lock, in a fresh session.
    with Session(identity.engine) as lookup:
        candidate = lookup.execute(
            select(ExportJob.request_id, DataRequest.user_id)
            .join(DataRequest, DataRequest.id == ExportJob.request_id)
            .outerjoin(ExportGeneration, ExportGeneration.id == ExportJob.generation_id)
            .where(
                or_(
                    (ExportJob.status == "QUEUED")
                    & (ExportJob.next_attempt_at <= identity.clock()),
                    (ExportJob.status == "RUNNING")
                    & (ExportGeneration.lease_until <= identity.clock()),
                )
            )
            .order_by(ExportJob.queued_at, ExportJob.request_id)
            .limit(1)
        ).first()
    if candidate is None:
        return None
    target, actor = candidate
    with Session(identity.engine) as db, db.begin():
        values = locked_job(identity, db, actor, target)
        if values is None:
            return None
        request, job = values
        now = identity.clock()
        if job.status == "RUNNING":
            generation = db.get(ExportGeneration, job.generation_id)
            if generation and generation.lease_until <= now:
                failed(identity, db, request, job, "PROCESSING_FAILED")
            return None
        if job.status != "QUEUED" or job.next_attempt_at is None or job.next_attempt_at > now:
            return None
        if request.completed_at or not grant_valid(identity, db, job) or job.attempts >= 3:
            failed(identity, db, request, job, "PROCESSING_FAILED")
            return None
        generation = ExportGeneration(
            id=uuid4(), request_id=target, created_at=now, lease_until=now + timedelta(seconds=180)
        )
        db.add(generation)
        db.flush()
        job.status, job.updated_at, job.generation_id = "RUNNING", now, generation.id
        job.attempts += 1
        job.next_attempt_at, job.failure = None, None
        db.flush()
        if job.grant_family is None or job.grant_authenticated_at is None:
            raise RuntimeError("Private export authorization unavailable")
        return ExportClaim(
            target,
            actor,
            generation.id,
            job.grant_family,
            job.grant_authenticated_at,
            job.correlation_id,
        )


def fail_claim(identity: IdentityService, claim: ExportClaim, reason: ExportFailure) -> bool:
    with Session(identity.engine) as db, db.begin():
        values = locked_job(identity, db, claim.actor_id, claim.request_id)
        if values is None:
            return False
        request, job = values
        if job.status != "RUNNING" or job.generation_id != claim.generation_id:
            return False
        failed(identity, db, request, job, reason)
        return True
