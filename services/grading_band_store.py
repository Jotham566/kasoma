"""Locked immutable band storage. No academic activation authority is exposed."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.domain.grading_bands import GradingBandRow
from services.short_text_eligibility import CalibrationBand, GradingScope

DisableReason = Literal["CRITICAL_ERROR", "AUDIT_AGREEMENT", "MANUAL"]


def register(db: Session, band: CalibrationBand, now: datetime) -> None:
    """Record trusted metadata disabled; never synthesize/authorize a real approval."""
    band = CalibrationBand.model_validate(band)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Calibration clock must be timezone-aware")
    if band.enabled:
        raise ValueError("Registration cannot enable scoring")
    values = band.model_dump(exclude={"scope"}) | band.scope.model_dump()
    db.add(
        GradingBandRow(
            **values,
            created_at=now,
            updated_at=now,
            activated_at=None,
            disabled_at=None,
            disable_reason=None,
            revision=1,
        )
    )
    db.flush()


def locked(db: Session, band_id: UUID) -> GradingBandRow:
    """Use within a transaction; publication must retain this lock through commit."""
    row = db.scalar(
        select(GradingBandRow)
        .where(GradingBandRow.id == band_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if row is None:
        raise ValueError("Calibration band unavailable")
    return row


def snapshot(row: GradingBandRow) -> CalibrationBand:
    scope = GradingScope.model_validate(
        {name: getattr(row, name) for name in GradingScope.model_fields}
    )
    return CalibrationBand.model_validate(
        {
            name: scope if name == "scope" else getattr(row, name)
            for name in CalibrationBand.model_fields
        }
    )


def disable(db: Session, band_id: UUID, now: datetime, reason: DisableReason) -> bool:
    if reason not in {"CRITICAL_ERROR", "AUDIT_AGREEMENT", "MANUAL"}:
        raise ValueError("Unknown band disablement reason")
    row = locked(db, band_id)
    if row.disabled_at is not None:
        return False
    if now.tzinfo is None or now.utcoffset() is None or now < row.updated_at:
        raise ValueError("Invalid band disablement time")
    row.enabled = False
    row.disabled_at = row.updated_at = now
    row.disable_reason = reason
    row.revision += 1
    db.flush()
    return True
