"""FR-OPS-002: bounded payload-free OTP adapter observations."""

from dataclasses import replace
from time import time_ns

import pytest

from services.metric_reader import DeltaReader
from services.otp_metrics import MAX_COUNT, OTPInterval, OTPMetrics, project


@pytest.fixture
def metric():
    reader = DeltaReader()
    owned = OTPMetrics(reader)
    yield owned, reader
    owned.shutdown()


def test_actual_sdk_four_outcomes_delta_and_current_observation_time(metric):
    owned, reader = metric
    assert owned.take(reader) is None
    before = time_ns()
    for kind in ["EMAIL", "SMS"]:
        for outcome in ["RETURNED", "FAILED"]:
            owned.record(kind, outcome)
    frame = owned.take(reader)
    assert frame.start_ns >= before and frame.counts == (1, 1, 1, 1)
    assert OTPInterval.decode(frame.encode()) == frame
    assert owned.take(reader) is None
    owned.record("SMS", "FAILED")
    assert owned.take(reader).counts == (0, 0, 0, 1)


@pytest.mark.parametrize(
    "counts", [(True, 0, 0, 0), (0,) * 3, [0] * 4, (-1, 0, 0, 0), (MAX_COUNT, 1, 0, 0)]
)
def test_strict_bounded_immutable_counts(counts):
    with pytest.raises(ValueError):
        OTPInterval(1, 2, counts)


@pytest.mark.parametrize(
    "body",
    [
        b"{}",
        b"x" * 1025,
        b'{"v":1,"start_ns":1,"end_ns":2,"counts":[0,0,0,0],"recipient":"CANARY"}',
        b'{"v":1,"v":1,"start_ns":1,"end_ns":2,"counts":[0,0,0,0]}',
    ],
)
def test_canonical_closed_codec(body):
    with pytest.raises(ValueError, match="^INVALID_OTP_INTERVAL$"):
        OTPInterval.decode(body)


def test_unowned_scope_labels_and_missing_observations_are_rejected(metric):
    owned, reader = metric
    owned.record("EMAIL", "RETURNED")
    data = reader.take()
    resource = data.resource_metrics[0]
    scope = resource.scope_metrics[0]
    series = scope.metrics[0]
    point = series.data.data_points[0]
    bad = replace(
        series,
        data=replace(series.data, data_points=[replace(point, attributes={"recipient": "CANARY"})]),
    )
    with pytest.raises(ValueError, match="^INVALID_OTP_POINT$"):
        project(
            replace(
                data,
                resource_metrics=[
                    replace(
                        resource, scope_metrics=[replace(scope, metrics=[bad, *scope.metrics[1:]])]
                    )
                ],
            ),
            owned.start_ns,
            1,
        )
    with pytest.raises(ValueError, match="^INCOHERENT_OTP_COLLECTION$"):
        project(data, owned.start_ns, 2)


def test_otp_collector_failure_and_shutdown_do_not_log_payloads(caplog):
    from unittest.mock import Mock

    from services.otp_metric_collector import OTPMetricCollector

    store = Mock()
    store.pulse.side_effect = RuntimeError("CANARY-credentials")
    store.write.side_effect = RuntimeError("CANARY-code")
    store.cache.close.side_effect = RuntimeError("CANARY-endpoint")
    collector = OTPMetricCollector(store)
    assert not collector.collect_once()
    collector.metrics.record("SMS", "FAILED")
    assert not collector.collect_once()
    collector.start()
    collector.close()
    collector.close()
    store.cache.close.assert_called_once()
    assert not collector.thread.is_alive()
    assert "CANARY" not in caplog.text


@pytest.mark.parametrize("environment,enabled", [("production", True), ("test", False)])
def test_disabled_or_production_app_never_constructs_otp_collector(
    settings, environment, enabled, monkeypatch
):
    from unittest.mock import Mock

    from fastapi.testclient import TestClient

    from apps.api.main import create_app

    factory = Mock(side_effect=AssertionError("must not construct"))
    request_collector = Mock()
    config = settings.model_copy(
        update={"app_env": environment, "otp_observation_enabled": enabled}
    )
    with TestClient(
        create_app(config, metrics_factory=lambda _: request_collector, otp_metrics_factory=factory)
    ) as client:
        assert client.get("/api/v1/live").status_code == 200
        assert client.app.state.otp_observer is None
    factory.assert_not_called()
    from types import SimpleNamespace

    from services.operations import otp_dispatch

    connect = Mock()
    monkeypatch.setattr("services.operations.metric_cache", connect)
    assert otp_dispatch(SimpleNamespace(settings=config)) is None
    connect.assert_not_called()


def test_app_local_otp_lifecycle_and_failed_startup_are_private(settings, caplog):
    from unittest.mock import Mock

    from fastapi.testclient import TestClient

    from apps.api.main import create_app

    config = settings.model_copy(update={"app_env": "test", "otp_observation_enabled": True})
    first, second = Mock(), Mock()

    def app(collector):
        return create_app(
            config, metrics_factory=lambda _: Mock(), otp_metrics_factory=lambda _: collector
        )

    a, b = app(first), app(second)
    with TestClient(a), TestClient(b):
        assert a.state.otp_observer is first.metrics
        assert b.state.otp_observer is second.metrics
    for value in [first, second]:
        value.start.assert_called_once()
        value.close.assert_called_once()
    failed = Mock(side_effect=RuntimeError("CANARY-startup"))
    with TestClient(
        create_app(config, metrics_factory=lambda _: Mock(), otp_metrics_factory=failed)
    ) as client:
        assert client.get("/api/v1/live").status_code == 200
        assert client.app.state.otp_observer is None
    assert "CANARY" not in caplog.text


def test_local_failure_threshold_boundary_and_recovery():
    from services.health import Health
    from services.operations import evaluate
    from services.operations_contracts import OperationThresholds, OTPDispatch

    health = Health(status="ok", database="up", redis="up")
    limits = OperationThresholds(
        failed_imports=1, import_age_seconds=300, unresolved_flags=20, otp_failures=2
    )
    for failures, expected in [(1, False), (2, True), (0, False)]:
        sample = OTPDispatch(
            observed_attempts=failures,
            email_returned=0,
            email_failed=failures,
            sms_returned=0,
            sms_failed=0,
            interval_count=1,
            capped=False,
        )
        alerts = evaluate(health, "up", None, limits, otp_metric=sample)
        assert ("OTP_ADAPTER_FAILURES" in {a.code for a in alerts}) is expected


def test_partial_collector_start_and_failed_cleanup_cannot_block_api(settings, caplog):
    from unittest.mock import Mock

    from fastapi.testclient import TestClient

    from apps.api.main import create_app

    config = settings.model_copy(update={"app_env": "test", "otp_observation_enabled": True})
    broken = Mock()
    broken.start.side_effect = RuntimeError("CANARY-start")
    broken.close.side_effect = RuntimeError("CANARY-close")
    with TestClient(
        create_app(config, metrics_factory=lambda _: Mock(), otp_metrics_factory=lambda _: broken)
    ) as client:
        assert client.get("/api/v1/live").status_code == 200
        assert client.app.state.otp_observer is None
    broken.close.assert_called_once()
    assert "CANARY" not in caplog.text
