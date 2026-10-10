"""One-claim grading transitions; persistence must lock and publish atomically (ADR-050)."""

from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, ConfigDict, model_validator

from services.short_text_validation import StrictContract

QUEUE_LIMIT = timedelta(minutes=5)
LEASE_LIMIT = timedelta(seconds=30)
Reason = Literal["QUEUE_EXPIRED", "WORKER_EXPIRED", "NOT_ELIGIBLE", "GRADING_FAILED"]


class WorkflowError(RuntimeError):
    """Closed transition error, safe to map to a minimized operational code."""


class GradingWork(StrictContract):
    model_config = ConfigDict(frozen=True)
    attempt_id: UUID
    status: Literal["QUEUED", "RUNNING", "GRADED", "LOW_CONFIDENCE"] = "QUEUED"
    queued_at: AwareDatetime
    claim_id: UUID | None = None
    claimed_at: AwareDatetime | None = None
    lease_until: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None
    reason: Reason | None = None

    @model_validator(mode="after")
    def coherent(self) -> "GradingWork":
        claimed = self.claim_id is not None
        if claimed != (self.claimed_at is not None) or claimed != (self.lease_until is not None):
            raise ValueError("Incomplete claim")
        if self.claimed_at is not None and self.lease_until is not None:
            if not self.queued_at <= self.claimed_at < self.queued_at + QUEUE_LIMIT:
                raise ValueError("Claim outside queue window")
            if self.lease_until != min(self.claimed_at + LEASE_LIMIT, self.queued_at + QUEUE_LIMIT):
                raise ValueError("Invalid lease deadline")
        if (
            self.status == "QUEUED"
            and claimed
            or self.status in {"RUNNING", "GRADED"}
            and not claimed
        ):
            raise ValueError("Claim does not match status")
        terminal = self.status in {"GRADED", "LOW_CONFIDENCE"}
        if terminal != (self.finished_at is not None):
            raise ValueError("Completion does not match status")
        if (self.status == "LOW_CONFIDENCE") != (self.reason is not None):
            raise ValueError("Neutral reason does not match status")
        if self.finished_at is not None:
            if self.finished_at < (self.claimed_at or self.queued_at):
                raise ValueError("Completion precedes work")
            deadline = self.lease_until if claimed else self.queued_at + QUEUE_LIMIT
            if deadline is None:
                raise ValueError("Missing claim deadline")
            if self.reason in {"QUEUE_EXPIRED", "WORKER_EXPIRED"}:
                if self.finished_at < deadline or (self.reason == "WORKER_EXPIRED") != claimed:
                    raise ValueError("Invalid expiry outcome")
            elif not claimed or self.finished_at >= deadline:
                raise ValueError("Publication outside live claim")
        return self


def checked(work: GradingWork, now: datetime) -> GradingWork:
    try:
        valid = GradingWork.model_validate(work.model_dump())
        observed = valid.finished_at or valid.claimed_at or valid.queued_at
        if now.tzinfo is None or now.utcoffset() is None or now < observed:
            raise ValueError("Invalid clock")
        return valid
    except Exception:
        raise WorkflowError("GRADING_STATE_INVALID") from None


def revised(work: GradingWork, **changes: object) -> GradingWork:
    return GradingWork.model_validate(work.model_dump() | changes)


def expire_work(work: GradingWork, now: datetime) -> GradingWork:
    """Terminal jobs remain unchanged. Expiry never renews a model-call budget."""
    work = checked(work, now)
    if work.status == "QUEUED" and now >= work.queued_at + QUEUE_LIMIT:
        return revised(work, status="LOW_CONFIDENCE", finished_at=now, reason="QUEUE_EXPIRED")
    if work.status == "RUNNING" and work.lease_until is not None and now >= work.lease_until:
        return revised(work, status="LOW_CONFIDENCE", finished_at=now, reason="WORKER_EXPIRED")
    return work


def claim_work(work: GradingWork, now: datetime, claim_id: UUID) -> GradingWork:
    work = expire_work(work, now)
    if not isinstance(claim_id, UUID):
        raise WorkflowError("GRADING_CLAIM_INVALID")
    if work.status != "QUEUED":
        raise WorkflowError("GRADING_NOT_CLAIMABLE")
    return revised(
        work,
        status="RUNNING",
        claim_id=claim_id,
        claimed_at=now,
        lease_until=min(now + LEASE_LIMIT, work.queued_at + QUEUE_LIMIT),
    )


def finish_work(
    work: GradingWork,
    now: datetime,
    claim_id: UUID,
    *,
    outcome: Literal["GRADED", "LOW_CONFIDENCE"],
    reason: Literal["NOT_ELIGIBLE", "GRADING_FAILED"] | None = None,
) -> GradingWork:
    """Caller must verify eligibility and atomically store grade/mastery or neutral fallback.

    This transition does not validate candidates, consent, ownership or academic evidence.
    It must never be used as a stand-alone authorization to score a learner.
    """
    work = checked(work, now)
    if (
        outcome not in {"GRADED", "LOW_CONFIDENCE"}
        or ((outcome == "LOW_CONFIDENCE") != (reason in {"NOT_ELIGIBLE", "GRADING_FAILED"}))
        or (outcome == "GRADED" and reason is not None)
    ):
        raise WorkflowError("GRADING_OUTCOME_INVALID")
    if work.claim_id != claim_id or work.claimed_at is None or now < work.claimed_at:
        raise WorkflowError("GRADING_STALE_CLAIM")
    if work.status in {"GRADED", "LOW_CONFIDENCE"}:
        if work.status == outcome and work.reason == reason:
            return work
        raise WorkflowError("GRADING_ALREADY_FINISHED")
    if work.status != "RUNNING" or work.lease_until is None or now >= work.lease_until:
        raise WorkflowError("GRADING_STALE_CLAIM")
    return revised(work, status=outcome, finished_at=now, reason=reason)
