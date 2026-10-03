"""FR-OPS-002: exact thresholds, recovery and safe alert output."""

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from apps.worker.main import make_worker
from services.config import Settings
from services.health import Health
from services.operations import emit_alerts, evaluate
from services.operations_contracts import (
    Count,
    OperationCounts,
    OperationsView,
    OperationThresholds,
)


def values(**changes):
    return OperationCounts(
        queued_imports=Count(value=0),
        oldest_import_seconds=0,
        failed_imports_24h=Count(value=0),
        unresolved_flags=Count(value=0),
        high_priority_flags=Count(value=0),
    ).model_copy(update=changes)


def test_operational_thresholds_exact_boundary_and_recovery():
    health = Health(status="ok", database="up", redis="up")
    limits = OperationThresholds(failed_imports=2, import_age_seconds=300, unresolved_flags=20)
    assert evaluate(health, "up", values(), limits) == []
    before = values(
        failed_imports_24h=Count(value=1),
        oldest_import_seconds=299,
        unresolved_flags=Count(value=19),
    )
    assert evaluate(health, "up", before, limits) == []
    at = values(
        failed_imports_24h=Count(value=2),
        oldest_import_seconds=300,
        unresolved_flags=Count(value=20),
        high_priority_flags=Count(value=1),
    )
    assert {a.code for a in evaluate(health, "up", at, limits)} == {
        "IMPORT_FAILED",
        "IMPORT_STALLED",
        "FLAG_BACKLOG",
        "HIGH_PRIORITY_FLAGS",
    }
    assert evaluate(health, "up", values(), limits) == []
    down = Health(status="degraded", database="down", redis="down")
    assert {a.code for a in evaluate(down, "unavailable", None, limits)} == {
        "DATABASE_DOWN",
        "REDIS_DOWN",
        "WORKER_HEARTBEAT_MISSING",
    }


def test_operational_alerts_are_allowlisted_metadata(caplog):
    health = Health(status="degraded", database="down", redis="down")
    limits = OperationThresholds(failed_imports=1, import_age_seconds=300, unresolved_flags=20)
    view = OperationsView(
        generated_at=datetime.now(UTC),
        health=health,
        worker="unavailable",
        counts=None,
        thresholds=limits,
        alerts=evaluate(health, "unavailable", None, limits),
    )
    request = uuid4()
    assert emit_alerts(view, request) == 3
    assert len([record for record in caplog.records if record.name == "kasoma"]) == 3
    for record in caplog.records:
        if record.name != "kasoma":
            continue
        message = json.loads(record.message)
        assert set(message) == {
            "event",
            "schema_version",
            "correlation_id",
            "channel",
            "code",
            "severity",
            "observed",
            "threshold",
        }
        assert message["correlation_id"] == str(request)
    assert "AI_USAGE" in view.unavailable_metrics


@pytest.mark.parametrize(
    "field, value",
    [
        ("ops_failed_import_threshold", 0),
        ("ops_import_age_seconds", 59),
        ("ops_flag_backlog_threshold", 10001),
    ],
)
def test_operational_limits_fail_closed(field, value):
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_operational_worker_schedule():
    app = make_worker(Settings())
    assert app.conf.beat_schedule["monitor-operations"] == {
        "task": "kasoma.monitor_operations",
        "schedule": 60.0,
    }
    assert "kasoma.monitor_operations" in app.tasks


@pytest.mark.parametrize(
    "task_name", ["kasoma.monitor_operations", "kasoma.content_imports", "kasoma.expire_exports"]
)
def test_worker_tasks_keep_their_own_application_settings(monkeypatch, task_name):
    """App factories must not reuse another app's database/credential closure."""
    observed = []

    class StopBeforeConnection(Exception):
        pass

    def capture(settings):
        observed.append(settings)
        raise StopBeforeConnection

    monkeypatch.setattr("apps.worker.main.engine_for", capture)
    first_settings = Settings()
    second_settings = first_settings.model_copy(update={"ops_flag_backlog_threshold": 21})
    first = make_worker(first_settings)
    second = make_worker(second_settings)
    try:
        for app, expected in [
            (first, first_settings),
            (second, second_settings),
            (first, first_settings),
        ]:
            with pytest.raises(StopBeforeConnection):
                app.tasks[task_name].run()
            assert observed[-1] is expected
    finally:
        first.close()
        second.close()
