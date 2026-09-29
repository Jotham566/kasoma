"""Owned, encrypted and expiring export snapshots with atomic completion evidence."""

import calendar
import hashlib
import json
import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.data_export_projection import project
from services.data_request_contracts import DataExportBundle
from services.data_requests import DataRequestService
from services.domain.data_requests import DataExport, DataRequest
from services.identity import IdentityError, IdentityService
from services.observability import emit

MAX_BYTES = 2 * 1024 * 1024


def retention_due(at: datetime) -> datetime:
    year = at.year + 6
    return at.replace(year=year, day=min(at.day, calendar.monthrange(year, at.month)[1]))


def download(
    identity: IdentityService, token: str, target: UUID, key: UUID, request_id: UUID
) -> DataExportBundle:
    service = DataRequestService(identity)
    with identity.transaction() as db:
        actor = identity.authenticate(db, token, recent=True).user_id
        if not identity.rate(db, f"data-export:{actor}", 10, 60):
            raise IdentityError("RATE_LIMITED", 429)
        row = db.scalar(select(DataRequest).where(DataRequest.id == target).with_for_update())
        if row is None or row.user_id != actor:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if row.kind != "EXPORT":
            raise IdentityError("EXPORT_REQUIRED", 409)
        fingerprint = identity.digest("data-request", "export:" + str(target))
        replay = service.replay(db, actor, key, fingerprint)
        artifact = db.get(DataExport, target)
        if row.completed_at:
            if artifact is None or artifact.expires_at <= identity.clock():
                raise IdentityError("EXPORT_EXPIRED", 410)
            raw = identity.decrypt(artifact.encrypted_payload)
            if hashlib.sha256(raw.encode()).hexdigest() != row.export_digest:
                raise RuntimeError("Export integrity check failed")
            bundle = DataExportBundle.model_validate_json(raw)
            if bundle.request_id != target:
                raise RuntimeError("Export binding check failed")
        else:
            bundle = project(identity, db, actor, target)
            raw = json.dumps(
                bundle.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            if len(raw.encode()) > MAX_BYTES:
                raise IdentityError("EXPORT_LIMIT_REACHED", 409)
            at = bundle.generated_at
            digest = hashlib.sha256(raw.encode()).hexdigest()
            db.add(
                DataExport(
                    request_id=target,
                    encrypted_payload=identity.encrypt(raw),
                    digest=digest,
                    created_at=at,
                    expires_at=at + timedelta(hours=24),
                )
            )
            db.flush()
            row.completed_at, row.retention_due_at, row.export_digest = (
                at,
                retention_due(at),
                digest,
            )
            db.flush()
            service.audit(db, actor, target, "data_export.completed", request_id)
            identity.event(db, actor, "data_export.completed", str(request_id))
        if replay is None:
            service.receipt(db, actor, key, fingerprint, row)
        service.audit(db, actor, target, "data_export.retrieved", request_id)
        return bundle


def expire(identity: IdentityService, request_id: UUID) -> int:
    # Aggregate metadata only. The payload is disposable; accountability rows remain intact.
    with Session(identity.engine) as db, db.begin():
        rows = list(
            db.scalars(
                select(DataExport)
                .where(DataExport.expires_at <= identity.clock())
                .order_by(DataExport.expires_at)
                .limit(100)
                .with_for_update(skip_locked=True)
            )
        )
        for row in rows:
            db.delete(row)
        count = len(rows)
    emit("data_export.expiry", str(request_id), "WORKER", 200)
    logging.getLogger("kasoma").info(
        json.dumps(
            {
                "event": "data_export.expiry_count",
                "correlation_id": str(request_id),
                "expired_count": count,
                "schema_version": 1,
            }
        )
    )
    return count
