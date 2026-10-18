"""Bounded local grading queue truth, never model cost or academic accuracy."""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.domain.grading_audits import GradingAuditAssignment, GradingAuditReview
from services.domain.grading_bands import GradingBandRow
from services.domain.grading_work import GradingWorkRow
from services.operations_contracts import GradingCounts


def grading_counts(db: Session, now: datetime) -> GradingCounts:
    from services.operations import bounded_count

    work = select(1).select_from(GradingWorkRow)
    pending = GradingWorkRow.status.in_(["QUEUED", "RUNNING"])
    oldest = db.scalar(select(func.min(GradingWorkRow.queued_at)).where(pending))
    recent = work.where(
        GradingWorkRow.finished_at >= now - timedelta(hours=24),
        GradingWorkRow.finished_at <= now,
    )
    return GradingCounts(
        queued=bounded_count(db, work.where(GradingWorkRow.status == "QUEUED")),
        running=bounded_count(db, work.where(GradingWorkRow.status == "RUNNING")),
        expired_running_leases=bounded_count(
            db, work.where(GradingWorkRow.status == "RUNNING", GradingWorkRow.lease_until <= now)
        ),
        oldest_pending_seconds=max(0, int((now - oldest).total_seconds())) if oldest else 0,
        graded_finished_24h=bounded_count(db, recent.where(GradingWorkRow.status == "GRADED")),
        neutral_finished_24h=bounded_count(
            db, recent.where(GradingWorkRow.status == "LOW_CONFIDENCE")
        ),
        processing_fallback_finished_24h=bounded_count(
            db,
            recent.where(
                GradingWorkRow.status == "LOW_CONFIDENCE", GradingWorkRow.reason == "GRADING_FAILED"
            ),
        ),
        pending_audits=bounded_count(
            db,
            select(1)
            .select_from(GradingAuditAssignment)
            .where(
                ~select(GradingAuditReview.id)
                .where(GradingAuditReview.id == GradingAuditAssignment.id)
                .exists()
            ),
        ),
        disabled_bands=bounded_count(
            db,
            select(1)
            .select_from(GradingBandRow)
            .where(
                GradingBandRow.disabled_at.is_not(None), GradingBandRow.activated_at.is_not(None)
            ),
        ),
    )
