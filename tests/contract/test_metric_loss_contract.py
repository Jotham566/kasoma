"""NFR-OBS-001: the loss marker has a finite closed range and no diagnostic payload."""

from unittest.mock import Mock

import pytest

from services.metric_interval_store import BoundedIntervalStore


@pytest.mark.parametrize("value", [0, -1, 300001, True, 1.2, "300000", None])
def test_invalid_marker_duration_never_reaches_redis(value):
    cache = Mock()
    store = BoundedIntervalStore(cache, "a" * 64, kind="request")
    with pytest.raises(ValueError, match="^INVALID_METRIC_LOSS_WINDOW$"):
        store.mark_loss(value)
    cache.eval.assert_not_called()


@pytest.mark.parametrize("kind", ["request", "model"])
def test_failed_loss_marker_is_republished_before_recovered_freshness(monkeypatch, kind, caplog):
    from services.model_metric_collector import ModelMetricCollector
    from services.request_metrics_collector import RequestMetricCollector

    store = Mock()
    store.write.return_value = False
    store.mark_loss.side_effect = RuntimeError("CANARY-redis-credentials")
    collector = RequestMetricCollector(store) if kind == "request" else ModelMetricCollector(store)
    monkeypatch.setattr(
        f"services.{kind}_metric{'s' if kind == 'request' else ''}_collector.monotonic",
        lambda: 100.0,
    )
    try:
        if kind == "request":
            collector.metrics.record(25)
        else:
            collector.metrics.record("LOW_CONFIDENCE", None, None)
        assert not collector.collect_once()
        assert collector.loss_until == 400
        calls = []
        store.mark_loss.side_effect = lambda value: calls.append(("gap", value))
        store.pulse.side_effect = lambda: calls.append(("fresh", None))
        assert collector.collect_once()
        assert calls == [("gap", 300000), ("fresh", None)]
        assert "CANARY" not in caplog.text
    finally:
        collector.close()
