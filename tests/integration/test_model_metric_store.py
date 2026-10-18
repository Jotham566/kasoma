"""Bounded synthetic Redis namespaces; preserve all unrelated application state."""

import hashlib
from dataclasses import replace
from uuid import uuid4

import pytest
from redis import Redis

from services.config import Settings
from services.metric_interval_store import MAX_INTERVALS, RETENTION_MS
from services.model_metric_collector import ModelMetricCollector
from services.model_metric_store import ModelMetricStore
from services.model_metrics import ModelInterval
from services.request_metrics_collector import metric_scope

pytestmark = pytest.mark.integration


@pytest.fixture
def store():
    with Redis.from_url(Settings().redis_url.get_secret_value(), socket_timeout=1) as cache:
        owned = ModelMetricStore(cache, hashlib.sha256(uuid4().bytes).hexdigest())
        yield owned
        keys = list(cache.scan_iter(match=owned.prefix + "*", count=300))
        if keys:
            cache.delete(*keys)


def frame(store, age_ms=0):
    seconds, micros = store.cache.time()
    end = (seconds * 1000 + micros // 1000 - 10 - age_ms) * 1_000_000
    return ModelInterval(end - 5_000_000_000, end, (1, 1, 1, 2, 100, 20))


def test_missing_fresh_empty_independent_sources_retry_and_conflict(store):
    assert store.read() is None
    store.pulse()
    assert store.read().counts == (0,) * 6
    item, source = frame(store), uuid4()
    assert store.write(source, item)
    expiry = store.cache.pexpiretime(store.interval_key(source, item))
    assert expiry == item.start_ns // 1_000_000 + RETENTION_MS
    assert store.write(source, item)
    assert store.cache.pexpiretime(store.interval_key(source, item)) == expiry
    assert store.write(uuid4(), item)
    assert store.read().counts == (2, 2, 2, 4, 200, 40)
    with pytest.raises(ValueError, match="^INVALID_METRIC_STORE$"):
        store.write(source, replace(item, counts=(2, 1, 1, 2, 100, 20)))
    store.cache.delete(store.fresh)
    assert store.read() is None


def test_expiry_future_cap_and_missing_unexpired_interval(store):
    assert not store.write(uuid4(), frame(store, RETENTION_MS))
    assert not store.write(uuid4(), frame(store, -60000))
    item = frame(store)
    for _ in range(MAX_INTERVALS + 1):
        assert store.write(uuid4(), item)
    value = store.read()
    assert value.capped and value.interval_count == MAX_INTERVALS
    assert value.counts == tuple(v * MAX_INTERVALS for v in item.counts)
    assert 0 < store.cache.pttl(store.capped) <= RETENTION_MS
    token = store.cache.zrange(store.registry, 0, 0)[0].decode()
    store.cache.delete(store.data_prefix + token)
    assert store.read() is None


@pytest.mark.parametrize("body", [b"{}", b"CANARY-private", b"x" * 1025])
def test_corrupt_payload_fails_closed_without_logging(store, caplog, body):
    item, source = frame(store), uuid4()
    assert store.write(source, item)
    store.cache.set(store.interval_key(source, item), body, keepttl=True)
    assert store.read() is None
    assert "CANARY" not in caplog.text


def test_collector_actual_sdk_empty_and_known_unknown_roundtrip(store):
    collector = ModelMetricCollector(store)
    try:
        assert collector.collect_once()
        assert store.read().counts == (0,) * 6
        collector.metrics.record("CANDIDATE", 1, 2)
        collector.metrics.record("LOW_CONFIDENCE", None, None)
        assert collector.collect_once()
        assert store.read().counts == (1, 1, 0, 1, 1, 2)
        assert collector.collect_once()
        assert store.read().counts == (1, 1, 0, 1, 1, 2)
    finally:
        collector.close()


def test_model_scope_isolated_from_request_and_host_aliases():
    settings = Settings()
    assert metric_scope(settings) != metric_scope(settings, purpose="model-metrics")
    other = settings.model_copy(update={"database_url": settings.database_url})
    assert metric_scope(settings, purpose="model-metrics") == metric_scope(
        other, purpose="model-metrics"
    )
