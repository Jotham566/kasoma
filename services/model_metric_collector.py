"""Owned worker SDK collection; bounded Redis export runs outside provider dispatch."""

from threading import Event, Thread
from uuid import uuid4

from services.config import Settings
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
        self.thread: Thread | None = None

    def collect_once(self) -> bool:
        try:
            frame = self.metrics.take(self.reader)
            if frame is None:
                self.store.pulse()
                return True
            return self.store.write(self.source, frame)
        except Exception:
            # Do not log SDK, Redis, endpoint or frame diagnostics.
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
