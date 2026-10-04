"""FR-OPS-002: bounded sampling, honest empty state and inclusive local alert thresholds."""

import pytest
from pydantic import ValidationError

from services.channel_operations import dispatch_timing
from services.config import Settings
from services.health import Health
from services.operations import evaluate
from services.operations_contracts import ChannelCounts, Count, DispatchTiming, OperationThresholds
from tests.contract.test_operations_contract import values


def channel(**changes):
    return ChannelCounts(
        queued_inbound=Count(value=0),
        queued_outbound=Count(value=0),
        oldest_pending_seconds=0,
        failed_inbound_received_24h=Count(value=0),
        rejected_inbound_received_24h=Count(value=0),
        failed_outbound_created_24h=Count(value=0),
        cancelled_outbound_created_24h=Count(value=0),
        accepted_outbound_created_24h=Count(value=0),
        feedback_dispatch=dispatch_timing([]),
    ).model_copy(update=changes)


def test_dispatch_percentile_empty_zero_rounding_and_cap():
    assert dispatch_timing([]).p95_ms is None
    assert dispatch_timing([0]).p95_ms == 0
    assert dispatch_timing([0.1]).p95_ms == 1
    assert dispatch_timing(list(reversed(range(100, 2100, 100)))).p95_ms == 1900
    timing = dispatch_timing([1000] * 1000 + [99999])
    assert timing.sample_size == 1000 and timing.sample_capped and timing.p95_ms == 1000


def test_channel_alert_boundary_minimum_sample_and_recovery():
    health = Health(status="ok", database="up", redis="up")
    limits = OperationThresholds(failed_imports=1, import_age_seconds=300, unresolved_flags=20)
    assert evaluate(health, "up", values(channel=channel()), limits) == []
    low = channel(
        oldest_pending_seconds=59,
        feedback_dispatch=DispatchTiming(sample_size=19, sample_capped=False, p95_ms=9999),
        rejected_inbound_received_24h=Count(value=100),
        cancelled_outbound_created_24h=Count(value=100),
    )
    assert evaluate(health, "up", values(channel=low), limits) == []
    high = channel(
        oldest_pending_seconds=60,
        failed_inbound_received_24h=Count(value=1),
        failed_outbound_created_24h=Count(value=1),
        feedback_dispatch=DispatchTiming(sample_size=20, sample_capped=False, p95_ms=1500),
    )
    assert {a.code for a in evaluate(health, "up", values(channel=high), limits)} == {
        "CHANNEL_INBOUND_FAILED",
        "CHANNEL_OUTBOUND_FAILED",
        "CHANNEL_STALLED",
        "CHANNEL_DISPATCH_SLOW",
    }
    high.feedback_dispatch.p95_ms = 1499
    assert "CHANNEL_DISPATCH_SLOW" not in {
        a.code for a in evaluate(health, "up", values(channel=high), limits)
    }
    assert evaluate(health, "up", values(channel=channel()), limits) == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("ops_channel_failure_threshold", 0),
        ("ops_channel_queue_age_seconds", 0),
        ("ops_channel_dispatch_p95_ms", 60001),
        ("ops_channel_dispatch_min_samples", 1001),
    ],
)
def test_channel_operational_configuration_fails_closed(field, value):
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_alert_schema_covers_the_emitted_contract_without_sensitive_fields():
    import json
    from pathlib import Path
    from typing import get_args

    from services.operations_contracts import AlertCode

    schema = json.loads(Path("packages/analytics-schema/operations-alert.schema.json").read_text())
    assert set(schema["properties"]["code"]["enum"]) == set(get_args(AlertCode))
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "event",
        "schema_version",
        "correlation_id",
        "channel",
        "code",
        "severity",
        "observed",
        "threshold",
    }
