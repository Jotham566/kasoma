"""Transactional work storage; callers own authorization and grading/publication policy."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from services.domain.assessment import Attempt
from services.domain.grading_work import GradingWorkRow
from services.short_text_workflow import (
    QUEUE_LIMIT,
    GradingWork,
    WorkflowError,
    claim_work,
    expire_work,
    finish_work,
)


def snapshot(row: GradingWorkRow) -> GradingWork:
    return GradingWork.model_validate(
        {name: getattr(row, name) for name in GradingWork.model_fields}
    )


def apply(db: Session, row: GradingWorkRow, result: GradingWork) -> None:
    if snapshot(row) == result:
        return
    for name, value in result.model_dump().items():
        setattr(row, name, value)
    row.revision += 1
    db.flush()


def enqueue(db: Session, attempt_id: UUID, correlation_id: UUID, now: datetime) -> GradingWork:
    """Caller must verify answer format/eligibility and enqueue in the attempt transaction."""
    attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id).with_for_update())
    if attempt is None:
        raise WorkflowError("GRADING_ATTEMPT_MISSING")
    existing = db.get(GradingWorkRow, attempt_id)
    if existing is not None:
        return snapshot(existing)
    state = GradingWork(attempt_id=attempt_id, queued_at=now)
    db.add(GradingWorkRow(**state.model_dump(), correlation_id=correlation_id, revision=1))
    db.flush()
    return state


def claim_next(db: Session, now: datetime) -> GradingWork | None:
    """Commit the returned claim before model dispatch; concurrent workers skip locked work."""
    row = db.scalar(
        select(GradingWorkRow)
        .where(
            GradingWorkRow.status == "QUEUED",
            GradingWorkRow.queued_at <= now,
            GradingWorkRow.queued_at > now - QUEUE_LIMIT,
        )
        .order_by(GradingWorkRow.queued_at, GradingWorkRow.attempt_id)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    if row is None:
        return None
    state = claim_work(snapshot(row), now, uuid4())
    apply(db, row, state)
    return state


def expire_due(db: Session, now: datetime, *, limit: int = 100) -> int:
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Expiry batch must be between 1 and 100")
    rows = db.scalars(
        select(GradingWorkRow)
        .where(
            or_(
                and_(
                    GradingWorkRow.status == "QUEUED", GradingWorkRow.queued_at <= now - QUEUE_LIMIT
                ),
                and_(GradingWorkRow.status == "RUNNING", GradingWorkRow.lease_until <= now),
            )
        )
        .order_by(GradingWorkRow.queued_at, GradingWorkRow.attempt_id)
        .with_for_update(skip_locked=True)
        .limit(limit)
    )
    count = 0
    for row in rows:
        apply(db, row, expire_work(snapshot(row), now))
        count += 1
    return count


def finish_neutral(
    db: Session, attempt_id: UUID, claim_id: UUID, now: datetime, *, failed: bool = False
) -> GradingWork:
    """No grade/mastery writer exists here. Services must separately authorize disclosure."""
    row = db.scalar(
        select(GradingWorkRow).where(GradingWorkRow.attempt_id == attempt_id).with_for_update()
    )
    if row is None:
        raise WorkflowError("GRADING_ATTEMPT_MISSING")
    result = finish_work(
        snapshot(row),
        now,
        claim_id,
        outcome="LOW_CONFIDENCE",
        reason="GRADING_FAILED" if failed else "NOT_ELIGIBLE",
    )
    apply(db, row, result)
    return result
