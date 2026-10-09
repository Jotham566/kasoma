"""Local Redis only, disposable synthetic namespaces; never flush shared state."""

import hashlib
from dataclasses import replace
from uuid import uuid4

import pytest
from redis import Redis

from services.config import Settings
from services.request_metrics import HistogramInterval
from services.request_metrics_collector import RequestMetricCollector
from services.request_metrics_store import MAX_INTERVALS, RETENTION_MS, RequestMetricStore

pytestmark = pytest.mark.integration


@pytest.fixture
def store():
    with Redis.from_url(
        Settings().redis_url.get_secret_value(), socket_connect_timeout=1, socket_timeout=1
    ) as cache:
        value = RequestMetricStore(cache, hashlib.sha256(uuid4().bytes).hexdigest())
        yield value
        # Only exact namespace created by this fixture; never another application's keys.
        keys = list(cache.scan_iter(match=value.prefix + "*", count=300))
        if keys:
            cache.delete(*keys)


def interval(store, *, age_ms=0, index=0):
    seconds, micros = store.cache.time()
    # Use millisecond precision and a small past margin, matching the storage clock.
    end = (seconds * 1000 + micros // 1000 - 10 - age_ms) * 1_000_000
    counts = [0] * 13
    counts[index] = 1
    return HistogramInterval(end - 5_000_000_000, end, tuple(counts))


def test_retry_is_idempotent_without_extending_absolute_retention(store):
    source = uuid4()
    item = interval(store)
    assert store.write(source, item)
    key = store.interval_key(source, item)
    expiry = store.cache.pexpiretime(key)
    assert expiry == item.start_ns // 1_000_000 + RETENTION_MS
    assert store.write(source, item)
    assert store.cache.pexpiretime(key) == expiry
    assert store.read().estimate.sample_size == 1
    assert store.cache.zcard(store.registry) == 1
    with pytest.raises(ValueError, match="^INVALID_METRIC_STORE$"):
        store.write(source, replace(item, counts=(2,) + (0,) * 12))
    assert store.read().estimate.sample_size == 1


def test_independent_producers_and_fresh_empty_are_distinct_from_missing(store):
    assert store.read() is None
    store.pulse()
    assert store.read().estimate.sample_size == 0
    assert store.read().observed_start_ns is None
    item = interval(store, index=6)
    assert store.write(uuid4(), item)
    assert store.write(uuid4(), item)
    snapshot = store.read()
    assert snapshot.estimate.sample_size == 2
    assert snapshot.estimate.p95_upper_inclusive_ms == 500
    assert snapshot.interval_count == 2
    assert snapshot.observed_start_ns == item.start_ns
    store.cache.delete(store.fresh)
    assert store.read() is None


def test_expired_and_future_collections_do_not_refresh_freshness(store):
    assert not store.write(uuid4(), interval(store, age_ms=RETENTION_MS))
    assert not store.write(uuid4(), interval(store, age_ms=-60000))
    assert store.read() is None
    assert store.cache.zcard(store.registry) == 0


def test_bounded_host_docker_clock_skew_does_not_extend_retention(store):
    item = interval(store, age_ms=-500)
    # A short real SDK interval can start slightly ahead of the Redis host clock.
    item = replace(item, start_ns=item.end_ns - 1_000_000)
    source = uuid4()
    assert store.write(source, item)
    key = store.interval_key(source, item)
    expiry = store.cache.pexpiretime(key)
    assert 0 < store.cache.pttl(key) <= RETENTION_MS
    assert store.read().estimate.sample_size == 1
    assert store.write(source, item)
    assert store.cache.pexpiretime(key) == expiry


def test_capacity_is_bounded_and_marked_without_touching_other_namespaces(store):
    other = RequestMetricStore(store.cache, hashlib.sha256(uuid4().bytes).hexdigest())
    other.pulse()
    try:
        item = interval(store)
        for _ in range(MAX_INTERVALS + 1):
            assert store.write(uuid4(), item)
        snapshot = store.read()
        assert snapshot.capped
        assert snapshot.interval_count == MAX_INTERVALS
        assert snapshot.estimate.sample_size == MAX_INTERVALS
        assert len(list(store.cache.scan_iter(match=store.data_prefix + "*"))) == MAX_INTERVALS
        assert 0 < store.cache.pttl(store.capped) <= RETENTION_MS
        assert other.read().estimate.sample_size == 0
    finally:
        store.cache.delete(other.fresh)


@pytest.mark.parametrize("fault", ["missing", "oversize", "invalid_json", "bad_member", "stale"])
def test_corruption_or_lost_data_is_unavailable_not_zero(store, fault):
    source = uuid4()
    item = interval(store)
    store.write(source, item)
    key = store.interval_key(source, item)
    if fault == "missing":
        store.cache.delete(key)
    elif fault == "oversize":
        store.cache.set(key, b"x" * 1025, px=1000)
    elif fault == "invalid_json":
        store.cache.set(key, b'{"secret":"CANARY"}', px=1000)
    elif fault == "bad_member":
        store.cache.zadd(store.registry, {"other:namespace": item.end_ns // 1_000_000 + 10000})
    else:
        store.cache.set(store.fresh, b"1", px=1000)
    assert store.read() is None


def test_expired_registry_entries_are_not_reported_as_lost_data(store):
    item = interval(store)
    source = uuid4()
    store.write(source, item)
    key = store.interval_key(source, item)
    store.cache.delete(key)
    store.cache.zadd(store.registry, {key.removeprefix(store.data_prefix): 1})
    assert store.read().estimate.sample_size == 0
    store.write(uuid4(), interval(store))
    assert store.cache.zcard(store.registry) == 1


def test_real_sdk_collector_publishes_only_observed_delta_counts(store):
    collector = RequestMetricCollector(store)
    try:
        assert collector.collect_once()
        assert store.read().estimate.sample_size == 0
        collector.metrics.record(499)
        collector.metrics.record(500)
        assert collector.collect_once()
        first = store.read()
        assert first.estimate.sample_size == 2
        assert first.estimate.p95_upper_inclusive_ms == 500
        collector.metrics.record(501)
        assert collector.collect_once()
        final = store.read()
        assert final.estimate.sample_size == 3
        assert final.estimate.p95_lower_exclusive_ms == 500
        assert final.estimate.p95_upper_inclusive_ms == 1000
        assert final.interval_count == 2
        for key in store.cache.scan_iter(match=store.data_prefix + "*"):
            raw = store.cache.get(key)
            assert len(raw) <= 1024
            assert store.cache.pttl(key) <= RETENTION_MS
            assert b"sum" not in raw and b"attributes" not in raw and b"trace" not in raw
    finally:
        collector.close()
