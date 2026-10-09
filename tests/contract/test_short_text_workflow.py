"""One-claim failure/replay semantics, using synthetic IDs and a deterministic clock."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

from services.short_text_workflow import (
    LEASE_LIMIT,
    QUEUE_LIMIT,
    GradingWork,
    WorkflowError,
    claim_work,
    expire_work,
    finish_work,
)

NOW = datetime(2026, 10, 10, tzinfo=UTC)
CLAIM = UUID(int=502)


@pytest.fixture
def queued():
    return GradingWork(attempt_id=UUID(int=501), queued_at=NOW)


def test_only_one_claim_and_no_lease_or_budget_renewal(queued):
    running = claim_work(queued, NOW, CLAIM)
    assert running.lease_until == NOW + LEASE_LIMIT
    for at in [NOW, NOW + timedelta(seconds=1), NOW + LEASE_LIMIT]:
        with pytest.raises(WorkflowError, match="NOT_CLAIMABLE"):
            claim_work(running, at, UUID(int=503))
    expired = expire_work(running, NOW + LEASE_LIMIT)
    assert expired.status == "LOW_CONFIDENCE" and expired.reason == "WORKER_EXPIRED"
    assert expired.claim_id == CLAIM
    assert expire_work(expired, NOW + QUEUE_LIMIT) == expired


def test_queue_expiry_is_inclusive_and_cannot_start_late(queued):
    assert expire_work(queued, NOW + QUEUE_LIMIT - timedelta(microseconds=1)) == queued
    expired = expire_work(queued, NOW + QUEUE_LIMIT)
    assert expired.reason == "QUEUE_EXPIRED" and expired.claim_id is None
    with pytest.raises(WorkflowError, match="NOT_CLAIMABLE"):
        claim_work(queued, NOW + QUEUE_LIMIT, CLAIM)


def test_late_queue_claim_has_only_remaining_absolute_budget(queued):
    at = NOW + QUEUE_LIMIT - timedelta(seconds=2)
    running = claim_work(queued, at, CLAIM)
    assert running.lease_until == NOW + QUEUE_LIMIT
    assert expire_work(running, NOW + QUEUE_LIMIT).reason == "WORKER_EXPIRED"


@pytest.mark.parametrize(
    "outcome,reason",
    [("GRADED", None), ("LOW_CONFIDENCE", "NOT_ELIGIBLE"), ("LOW_CONFIDENCE", "GRADING_FAILED")],
)
def test_terminal_replay_is_exact_and_does_not_rewrite_completion(queued, outcome, reason):
    running = claim_work(queued, NOW, CLAIM)
    result = finish_work(running, NOW + timedelta(seconds=1), CLAIM, outcome=outcome, reason=reason)
    assert finish_work(result, NOW + QUEUE_LIMIT, CLAIM, outcome=outcome, reason=reason) == result
    assert expire_work(result, NOW + QUEUE_LIMIT) == result
    with pytest.raises(WorkflowError, match="STALE_CLAIM"):
        finish_work(
            result, NOW + timedelta(seconds=2), UUID(int=504), outcome=outcome, reason=reason
        )


def test_old_worker_cannot_publish_at_or_after_expiry(queued):
    running = claim_work(queued, NOW, CLAIM)
    for delta in [LEASE_LIMIT, QUEUE_LIMIT]:
        with pytest.raises(WorkflowError, match="STALE_CLAIM"):
            finish_work(running, NOW + delta, CLAIM, outcome="GRADED")
    expired = expire_work(running, NOW + LEASE_LIMIT)
    with pytest.raises(WorkflowError, match="ALREADY_FINISHED"):
        finish_work(expired, NOW + LEASE_LIMIT, CLAIM, outcome="GRADED")


@pytest.mark.parametrize(
    "outcome,reason",
    [
        ("QUEUED", None),
        ("GRADED", "NOT_ELIGIBLE"),
        ("LOW_CONFIDENCE", None),
        ("LOW_CONFIDENCE", "QUEUE_EXPIRED"),
    ],
)
def test_untrusted_or_incoherent_outcomes_cannot_finish_work(queued, outcome, reason):
    with pytest.raises(WorkflowError, match="OUTCOME_INVALID"):
        finish_work(claim_work(queued, NOW, CLAIM), NOW, CLAIM, outcome=outcome, reason=reason)


def test_clock_regression_naive_clock_and_bypassed_state_are_rejected(queued):
    for at in [NOW - timedelta(seconds=1), NOW.replace(tzinfo=None)]:
        with pytest.raises(WorkflowError, match="STATE_INVALID"):
            claim_work(queued, at, CLAIM)
    running = claim_work(queued, NOW + timedelta(seconds=2), CLAIM)
    with pytest.raises(WorkflowError, match="STATE_INVALID"):
        finish_work(running, NOW, CLAIM, outcome="GRADED")
    corrupted = running.model_copy(update={"lease_until": NOW + QUEUE_LIMIT})
    with pytest.raises(WorkflowError, match="STATE_INVALID"):
        expire_work(corrupted, NOW)


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "RUNNING"},
        {"status": "GRADED", "finished_at": NOW},
        {"status": "LOW_CONFIDENCE", "finished_at": NOW, "reason": "QUEUE_EXPIRED"},
        {"claim_id": CLAIM},
        {"reason": "NOT_ELIGIBLE"},
    ],
)
def test_stored_snapshot_invariants_are_validated(queued, changes):
    with pytest.raises(ValidationError):
        GradingWork.model_validate(queued.model_dump() | changes)
