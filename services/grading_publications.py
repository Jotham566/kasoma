"""Atomic publication/audit ledger; callers still own scoring and authorization."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from services.domain.grading_audits import GradingPublication
from services.grading_band_store import locked


def publish(db: Session, band_id: UUID, attempt_id: UUID, now: datetime) -> GradingPublication:
    """Call in the grade/mastery transaction after all current eligibility checks.

    SQL allocates the ordinal and audit under the band lock. A replay returns the
    original ledger entry even after disablement; it cannot publish another grade.
    This substrate is format-independent and does not authorize model scoring.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Publication clock must be timezone-aware")
    band = locked(db, band_id)
    existing = db.get(GradingPublication, attempt_id)
    if existing is not None:
        if existing.band_id != band_id:
            raise ValueError("Conflicting publication binding")
        return existing
    if not band.enabled:
        raise ValueError("Calibration band disabled")
    row = GradingPublication(
        attempt_id=attempt_id,
        band_id=band_id,
        ordinal=0,
        audit_required=False,
        published_at=now,
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row
