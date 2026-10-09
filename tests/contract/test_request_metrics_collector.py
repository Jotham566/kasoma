"""Deterministic collector lifecycle and fake storage failure tests."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from apps.api.main import create_app
from services.health import Health
from services.operations import evaluate
from services.operations_contracts import OperationThresholds, RequestTiming
from services.request_metrics_collector import RequestMetricCollector, metric_cache, metric_scope


def test_collection_moves_only_delta_intervals_and_pulses_when_empty():
    store = Mock()
    store.write.return_value = True
    collector = RequestMetricCollector(store)
    try:
        assert collector.collect_once()
        store.pulse.assert_called_once()
        collector.metrics.record(123)
        assert collector.collect_once()
        first = store.write.call_args.args[1]
        assert sum(first.counts) == 1
        collector.metrics.record(600)
        assert collector.collect_once()
        second = store.write.call_args.args[1]
        assert sum(second.counts) == 1
        assert second.counts != first.counts
        assert first.end_ns == second.start_ns
    finally:
        collector.close()
    store.cache.close.assert_called_once()


def test_failures_do_not_log_secrets_or_escape_to_requests(caplog, capsys):
    store = Mock()
    store.pulse.side_effect = RuntimeError("CANARY-secret-endpoint")
    store.write.side_effect = RuntimeError("CANARY-private-payload")
    collector = RequestMetricCollector(store)
    try:
        assert not collector.collect_once()
        collector.metrics.record(10)
        assert not collector.collect_once()
        assert "CANARY" not in caplog.text + capsys.readouterr().out
    finally:
        collector.close()


def test_owned_thread_stops_without_collecting_or_contacting_redis():
    store = Mock()
    collector = RequestMetricCollector(store)
    collector.start()
    collector.close()
    assert not collector.thread.is_alive()
    store.write.assert_not_called()
    store.pulse.assert_not_called()


def test_scope_preserves_aliases_but_separates_schemas_and_keys(settings):
    baseline = metric_scope(settings)
    alias = settings.model_copy(
        update={
            "database_url": SecretStr("postgresql+psycopg://other:other@postgres:5432/synthetic")
        }
    )
    assert metric_scope(alias) == baseline
    for update in (
        {"database_url": SecretStr("postgresql+psycopg://s:s@localhost/other")},
        {
            "database_url": SecretStr(
                "postgresql+psycopg://s:s@localhost/synthetic?options=-csearch_path%3Dother"
            )
        },
        {"identity_lookup_key": SecretStr("another-key")},
    ):
        assert metric_scope(settings.model_copy(update=update)) != baseline


def test_redis_client_has_finite_io_and_no_implicit_retries(settings):
    cache = metric_cache(settings)
    try:
        options = cache.connection_pool.connection_kwargs
        assert options["socket_connect_timeout"] == 0.5
        assert options["socket_timeout"] == 0.5
        assert options["retry"].get_retries() == 0
        assert cache.connection_pool.max_connections == 1
    finally:
        cache.close()


@pytest.mark.parametrize("broken", [False, True])
def test_api_owns_collector_and_timing_failures_do_not_change_response(
    settings, monkeypatch, broken
):
    fake = Mock()
    if broken:
        fake.metrics.record.side_effect = RuntimeError("CANARY-secret")
    ticks = iter([1.0, 1.0124])
    monkeypatch.setattr("apps.api.main.perf_counter", lambda: next(ticks))
    with TestClient(create_app(settings, metrics_factory=lambda _: fake)) as client:
        response = client.get("/api/v1/live")
    assert response.status_code == 200
    fake.start.assert_called_once()
    fake.metrics.record.assert_called_once_with(13)
    fake.close.assert_called_once()
    assert "CANARY" not in response.text


@pytest.mark.parametrize(
    "lower,upper,samples,threshold,expected",
    [
        (250, 500, 20, 500, False),
        (500, 1000, 19, 500, False),
        (500, 1000, 20, 501, True),
        (500, 1000, 20, 502, False),
        (30000, None, 20, 30001, True),
        (None, None, 0, 500, False),
        (None, 0, 20, 1, False),
    ],
)
def test_latency_alert_requires_proven_integer_lower_bound(
    lower, upper, samples, threshold, expected
):
    timing = RequestTiming(
        sample_size=samples,
        p95_lower_exclusive_ms=lower,
        p95_upper_inclusive_ms=upper,
        interval_count=1,
        capped=False,
    )
    limits = OperationThresholds(
        failed_imports=1,
        import_age_seconds=300,
        unresolved_flags=20,
        request_p95_ms=threshold,
        request_min_samples=20,
    )
    health = Health(status="ok", database="up", redis="up")
    alerts = evaluate(health, "up", None, limits, timing)
    assert bool(alerts) is expected
    if expected:
        assert alerts[0].code == "REQUEST_RESPONSE_START_SLOW"
        assert alerts[0].observed == lower + 1
    assert evaluate(health, "up", None, limits, None) == []
