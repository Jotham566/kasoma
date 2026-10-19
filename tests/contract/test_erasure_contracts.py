"""ADR-061: reject expanded authority, stale formats and fabricated lifecycle states."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.erasure_contracts import ErasureAuthorization, ErasurePlan, ErasureStatus

NOW = datetime(2026, 10, 20, tzinfo=UTC)


def command():
    return {
        "plan_id": str(uuid4()),
        "plan_version": "a" * 64,
        "decision_reference": str(uuid4()),
        "affirmative": True,
    }


@pytest.mark.parametrize("value", [False, 0, 1, "true", "yes", None])
def test_authorization_requires_literal_boolean_confirmation(value):
    with pytest.raises(ValidationError):
        ErasureAuthorization.model_validate(command() | {"affirmative": value})


@pytest.mark.parametrize(
    "field",
    ["subject_id", "table", "sql", "cutoff", "force", "skip_holds", "completed_at"],
)
def test_authorization_cannot_expand_case_plan_authority(field):
    with pytest.raises(ValidationError):
        ErasureAuthorization.model_validate(command() | {field: "forbidden"})


def test_authorization_round_trip_preserves_exact_plan_and_decision():
    value = command()
    assert ErasureAuthorization.model_validate(value).model_dump(mode="json") == value


@pytest.mark.parametrize("seconds", [-1, 0, 601, 86400])
def test_plan_refuses_unbounded_or_nonpositive_lifetime(seconds):
    with pytest.raises(ValidationError):
        plan(expires_at=NOW + timedelta(seconds=seconds))


def plan(**changes):
    return ErasurePlan.model_validate(
        {
            "request_id": uuid4(),
            "plan_id": uuid4(),
            "version": "b" * 64,
            "observed_at": NOW,
            "expires_at": NOW + timedelta(minutes=10),
            "authorization_available": False,
            "blockers": ["EXECUTION_DISABLED"],
        }
        | changes
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"authorization_available": True},
        {"blockers": []},
        {"blockers": ["EXECUTION_DISABLED", "EXECUTION_DISABLED"]},
        {"blockers": ["secret-provider-diagnostic"]},
        {"observed_at": NOW.replace(tzinfo=None)},
        {"expires_at": NOW.replace(tzinfo=None)},
        {"version": "A" * 64},
        {"version": "a" * 63},
        {"manifest": "erasure-0042-v1"},
        {"policy": "production-erasure"},
        {"subject_id": str(uuid4())},
        {"source_keys": ["private-retry-key"]},
    ],
)
def test_plan_refuses_false_clearance_unknown_formats_and_private_fields(changes):
    with pytest.raises(ValidationError):
        plan(**changes)


def test_plan_availability_does_not_imply_execution_or_case_completion():
    unavailable = plan()
    available = plan(authorization_available=True, blockers=[])
    assert unavailable.blockers == ["EXECUTION_DISABLED"]
    assert available.expires_at - available.observed_at == timedelta(minutes=10)
    assert not {"subject_id", "source_keys", "completed_at", "execution_enabled"} & set(
        available.model_dump()
    )


def status(**changes):
    return ErasureStatus.model_validate(
        {
            "request_id": uuid4(),
            "phase": "AUTHORIZED",
            "authorized_at": NOW,
        }
        | changes
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"phase": "BARRIER_APPLIED"},
        {"closed_at": NOW},
        {"phase": "COMPLETED", "closed_at": NOW},
        {"completed_at": NOW},
        {"phase": "FAILED"},
        {"phase": "BLOCKED"},
        {"failure": "raw-database-diagnostic"},
        {"blocker": "PROCESSOR_UNAVAILABLE", "failure": "BATCH_TIMEOUT"},
        {"phase": "BARRIER_APPLIED", "closed_at": NOW - timedelta(seconds=1)},
        {"phase": "COMPLETED", "closed_at": NOW, "completed_at": NOW, "failure": "BATCH_TIMEOUT"},
        {
            "phase": "COMPLETED",
            "closed_at": NOW,
            "completed_at": NOW,
            "blocker": "VERIFICATION_INCOMPLETE",
        },
        {
            "phase": "COMPLETED",
            "closed_at": NOW + timedelta(seconds=1),
            "completed_at": NOW,
        },
        {"authorized_at": NOW.replace(tzinfo=None)},
        {"closed_at": NOW.replace(tzinfo=None)},
        {"contact": "synthetic-secret"},
        {"cursor": str(uuid4())},
    ],
)
def test_status_cannot_fabricate_closure_completion_or_expose_private_progress(changes):
    with pytest.raises(ValidationError):
        status(**changes)


@pytest.mark.parametrize("phase", ["BARRIER_APPLIED", "PRESERVING", "REMOVING", "VERIFYING"])
def test_blocked_and_failed_status_preserve_last_durable_phase(phase):
    blocked = status(phase=phase, closed_at=NOW, blocker="PRESERVATION_INCOMPLETE")
    failed = status(phase=phase, closed_at=NOW, failure="BATCH_TIMEOUT")
    assert blocked.phase == failed.phase == phase
    assert blocked.completed_at is failed.completed_at is None


def test_completed_status_requires_chronology_and_no_blocker_or_failure():
    result = status(phase="COMPLETED", closed_at=NOW, completed_at=NOW + timedelta(seconds=1))
    assert result.completed_at > result.closed_at
    assert result.failure is result.blocker is None
