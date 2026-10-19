"""FR-OPS-002/NFR-OBS-001: an empty pulse cannot hide known export loss."""

import hashlib
from uuid import uuid4

import pytest
from redis import Redis

from services.config import Settings
from services.metric_interval_store import RETENTION_MS
from services.model_metric_collector import ModelMetricCollector
from services.model_metric_store import ModelMetricStore
from services.otp_metric_collector import OTPMetricCollector
from services.otp_metric_store import OTPMetricStore
from services.request_metrics_collector import RequestMetricCollector
from services.request_metrics_store import RequestMetricStore

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("kind", ["request", "model", "otp"])
def test_unacknowledged_export_cannot_recover_as_measured_zero(monkeypatch, kind):
    with Redis.from_url(Settings().redis_url.get_secret_value(), socket_timeout=1) as cache:
        scope = hashlib.sha256(uuid4().bytes).hexdigest()
        store_class = {
            "request": RequestMetricStore,
            "model": ModelMetricStore,
            "otp": OTPMetricStore,
        }[kind]
        collector_class = {
            "request": RequestMetricCollector,
            "model": ModelMetricCollector,
            "otp": OTPMetricCollector,
        }[kind]
        store = store_class(cache, scope)
        collector = collector_class(store)

        def record():
            if kind == "request":
                collector.metrics.record(25)
            elif kind == "model":
                collector.metrics.record("LOW_CONFIDENCE", None, None)
            else:
                collector.metrics.record("EMAIL", "RETURNED")

        try:
            assert collector.collect_once()
            record()
            original = store.write
            monkeypatch.setattr(store, "write", lambda *args: False)
            assert not collector.collect_once()
            assert store.read() is None
            monkeypatch.setattr(store, "write", original)
            assert collector.collect_once()
            assert store.read() is None
            gap = store.prefix + "incomplete"
            expiry = cache.pexpiretime(gap)
            assert 0 < cache.pttl(gap) <= RETENTION_MS
            store.mark_loss(1)
            assert cache.pexpiretime(gap) >= expiry - 2
            record()
            assert collector.collect_once()
            assert cache.zcard(store.registry) == 1
            assert store.read() is None
            # Controlled expiry only in this owned namespace, not a real five-minute soak.
            collector.loss_until = 0
            cache.pexpireat(gap, 1)
            assert collector.collect_once()
            snapshot = store.read()
            assert snapshot is not None
            if kind == "request":
                assert snapshot.estimate.sample_size == 1
            elif kind == "model":
                assert snapshot.counts[:3] == (0, 1, 0)
            else:
                assert snapshot.counts == (1, 0, 0, 0)
        finally:
            try:
                collector.close()
                assert not collector.collect_once()
            finally:
                keys = list(cache.scan_iter(match=store.prefix + "*", count=300))
                if keys:
                    cache.delete(*keys)


def test_loss_marker_does_not_poison_other_metric_kinds():
    with Redis.from_url(Settings().redis_url.get_secret_value(), socket_timeout=1) as cache:
        scope = hashlib.sha256(uuid4().bytes).hexdigest()
        stores = [
            RequestMetricStore(cache, scope),
            ModelMetricStore(cache, scope),
            OTPMetricStore(cache, scope),
        ]
        try:
            for store in stores:
                store.pulse()
                assert store.read() is not None
            stores[0].mark_loss(300000)
            assert stores[0].read() is None
            assert stores[1].read() is not None and stores[2].read() is not None
        finally:
            for store in stores:
                keys = list(cache.scan_iter(match=store.prefix + "*", count=300))
                if keys:
                    cache.delete(*keys)
