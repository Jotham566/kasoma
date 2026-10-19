"""Owned worker SDK collection; bounded Redis export runs outside provider dispatch."""

from math import ceil
from threading import Event, Thread
from time import monotonic
from uuid import uuid4

from services.config import Settings
from services.metric_interval_store import RETENTION_MS
from services.metric_reader import DeltaReader
from services.model_metric_store import ModelMetricStore
from services.model_metrics import ModelMetrics
from services.request_metrics_collector import metric_cache, metric_scope


def create_collector(settings: Settings) -> "ModelMetricCollector":
    return ModelMetricCollector(
        ModelMetricStore(metric_cache(settings), metric_scope(settings, purpose="model-metrics"))
    )


class ModelMetricCollector:
    def __init__(self, store: ModelMetricStore) -> None:
        self.store = store
        self.reader = DeltaReader()
        self.metrics = ModelMetrics(self.reader)
        self.source = uuid4()
        self.stopping = Event()
        self.loss_until = 0.0
        self.thread: Thread | None = None

    def collect_once(self) -> bool:
        """Known export loss is unavailable, never a newly measured zero."""
        if self.stopping.is_set():
            return False
        try:
            interval = self.metrics.take(self.reader)
            if self.loss_until > monotonic():
                self.store.mark_loss(
                    max(1, min(RETENTION_MS, ceil((self.loss_until - monotonic()) * 1000)))
                )
            if interval is None:
                self.store.pulse()
                return True
            if not self.store.write(self.source, interval):
                raise ValueError("METRIC_EXPORT_UNAVAILABLE")
            return True
        except Exception:
            self.loss_until = monotonic() + RETENTION_MS / 1000
            try:
                self.store.mark_loss(RETENTION_MS)
            except Exception:
                return False
            return False

    def start(self) -> None:
        if self.thread is not None or self.stopping.is_set():
            raise RuntimeError("MODEL_COLLECTOR_ALREADY_STARTED")

        def run() -> None:
            while not self.stopping.wait(5):
                self.collect_once()

        self.thread = Thread(target=run, name="kasoma-model-metrics", daemon=True)
        self.thread.start()

    def close(self) -> None:
        self.stopping.set()
        if self.thread is not None:
            self.thread.join(timeout=3)
            if self.thread.is_alive():
                return
        self.metrics.shutdown()
        self.store.cache.close()
