"""Bounded removal of already-expired ephemeral authentication records only."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.domain.identity import Challenge, RateBucket
from services.observability import logger

if TYPE_CHECKING:
    from services.identity import IdentityService

BATCH_SIZE = 100


def expire_rows(db: Session, at: datetime) -> dict[str, int]:
    """Caller owns the transaction; row locks coordinate verification and rate refresh."""
    challenges = list(
        db.scalars(
            select(Challenge)
            .where(Challenge.expires_at <= at)
            .order_by(Challenge.expires_at, Challenge.id)
            .limit(BATCH_SIZE)
            .with_for_update(skip_locked=True)
        )
    )
    buckets = list(
        db.scalars(
            select(RateBucket)
            .where(RateBucket.expires_at <= at)
            .order_by(RateBucket.expires_at, RateBucket.key)
            .limit(BATCH_SIZE)
            .with_for_update(skip_locked=True)
        )
    )
    for row in challenges:
        db.delete(row)
    for bucket in buckets:
        db.delete(bucket)
    db.flush()
    return {"challenges": len(challenges), "rate_buckets": len(buckets)}


def expire_identity(identity: IdentityService, request_id: UUID) -> dict[str, int]:
    try:
        with Session(identity.engine) as db, db.begin():
            counts = expire_rows(db, identity.clock())
    except Exception:
        logger.warning(
            json.dumps(
                {
                    "event": "identity.ephemeral_expiry",
                    "correlation_id": str(request_id),
                    "status": "FAILED",
                    "challenges": 0,
                    "rate_buckets": 0,
                    "schema_version": 1,
                }
            )
        )
        raise RuntimeError("Ephemeral identity expiry failed; diagnostics withheld") from None
    logger.info(
        json.dumps(
            {
                "event": "identity.ephemeral_expiry",
                "correlation_id": str(request_id),
                "status": "SUCCEEDED",
                **counts,
                "schema_version": 1,
            }
        )
    )
    return counts
