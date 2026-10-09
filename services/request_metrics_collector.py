"""Owned local collection lifecycle; no Redis I/O on the request path."""

import hashlib
import hmac
import json
from threading import Event, Thread
from uuid import uuid4

from opentelemetry.sdk.metrics import Histogram
from opentelemetry.sdk.metrics.export import AggregationTemporality, MetricReader, MetricsData
from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from sqlalchemy.engine import make_url

from services.config import Settings
from services.request_metrics import RequestMetrics, project
from services.request_metrics_store import RequestMetricStore


def metric_scope(settings: Settings) -> str:
    url = make_url(settings.database_url.get_secret_value())
    scope = json.dumps(
        {"database": url.database, "options": url.query.get("options", "")}, sort_keys=True
    )
    return hmac.new(
        settings.identity_lookup_key.get_secret_value().encode(),
        ("request-metrics:" + scope).encode(),
        hashlib.sha256,
    ).hexdigest()


def metric_cache(settings: Settings) -> Redis:
    return Redis.from_url(
        settings.redis_url.get_secret_value(),
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
        retry=Retry(NoBackoff(), 0),
        max_connections=1,
    )


def create_collector(settings: Settings) -> "RequestMetricCollector":
    return RequestMetricCollector(
        RequestMetricStore(metric_cache(settings), metric_scope(settings))
    )


def record_timing(metrics: RequestMetrics | None, duration_ms: int) -> bool:
    try:
        if metrics is None:
            return False
        metrics.record(duration_ms)
        return True
    except Exception:
        return False


class DeltaReader(MetricReader):
    def __init__(self) -> None:
        super().__init__(preferred_temporality={Histogram: AggregationTemporality.DELTA})
        self.batch: MetricsData | None = None

    def _receive_metrics(
        self, metrics_data: MetricsData, timeout_millis: float = 1000, **kwargs: object
    ) -> None:
        self.batch = metrics_data

    def take(self) -> MetricsData | None:
        self.batch = None
        self.collect(timeout_millis=1000)
        result, self.batch = self.batch, None
        return result

    def shutdown(self, timeout_millis: float = 2000, **kwargs: object) -> None:
        self.batch = None


class RequestMetricCollector:
    def __init__(self, store: RequestMetricStore) -> None:
        self.store = store
        self.reader = DeltaReader()
        self.metrics = RequestMetrics(self.reader)
        self.source = uuid4()
        self.stopping = Event()
        self.thread: Thread | None = None

    def collect_once(self) -> bool:
        """Best-effort observed intervals, never an authoritative request ledger."""
        try:
            batch = self.reader.take()
            interval = project(batch) if batch is not None else None
            if interval is None:
                self.store.pulse()
                return True
            return self.store.write(self.source, interval)
        except Exception:
            # SDK/Redis errors may include endpoint or payload details. Freshness
            # expires naturally; requests never wait for or fail on this operation.
            return False

    def start(self) -> None:
        if self.thread is not None or self.stopping.is_set():
            raise RuntimeError("METRIC_COLLECTOR_ALREADY_STARTED")

        def run() -> None:
            while not self.stopping.wait(5):
                self.collect_once()

        self.thread = Thread(target=run, name="kasoma-request-metrics", daemon=True)
        self.thread.start()

    def close(self) -> None:
        self.stopping.set()
        if self.thread is not None:
            self.thread.join(timeout=3)
            if self.thread.is_alive():
                # Do not concurrently destroy SDK/Redis state used by a stuck worker.
                # The daemon cannot hold process shutdown; retained data still expires.
                return
        self.metrics.shutdown()
        self.store.cache.close()
