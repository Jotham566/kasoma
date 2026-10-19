"""Owned API OTP SDK collection; bounded Redis export runs outside provider dispatch."""

from math import ceil
from threading import Event, Thread
from time import monotonic
from uuid import uuid4

from services.config import Settings
from services.metric_interval_store import RETENTION_MS
from services.metric_reader import DeltaReader
from services.otp_metric_store import OTPMetricStore
from services.otp_metrics import OTPMetrics
from services.request_metrics_collector import metric_cache, metric_scope


def create_collector(settings: Settings) -> "OTPMetricCollector":
    return OTPMetricCollector(
        OTPMetricStore(metric_cache(settings), metric_scope(settings, purpose="otp-metrics"))
    )


class OTPMetricCollector:
    def __init__(self, store: OTPMetricStore) -> None:
        self.store = store
        self.reader = DeltaReader()
        self.metrics = OTPMetrics(self.reader)
        self.source = uuid4()
        self.stopping = Event()
        self.loss_until = 0.0
        self.thread: Thread | None = None

    def collect_once(self) -> bool:
        if self.stopping.is_set():
            return False
        try:
            frame = self.metrics.take(self.reader)
            if self.loss_until > monotonic():
                self.store.mark_loss(
                    max(1, min(RETENTION_MS, ceil((self.loss_until - monotonic()) * 1000)))
                )
            if frame is None:
                self.store.pulse()
                return True
            if not self.store.write(self.source, frame):
                raise ValueError("OTP_EXPORT_UNAVAILABLE")
            return True
        except Exception:
            # A recovered empty pulse must not turn known loss into measured zero.
            self.loss_until = monotonic() + RETENTION_MS / 1000
            try:
                self.store.mark_loss(RETENTION_MS)
            except Exception:
                return False
            return False

    def start(self) -> None:
        if self.thread is not None or self.stopping.is_set():
            raise RuntimeError("OTP_COLLECTOR_ALREADY_STARTED")

        def run() -> None:
            while not self.stopping.wait(5):
                self.collect_once()

        self.thread = Thread(target=run, name="kasoma-otp-metrics", daemon=True)
        self.thread.start()

    def close(self) -> None:
        if self.stopping.is_set():
            return
        self.stopping.set()
        try:
            if self.thread is not None and self.thread.ident is not None:
                self.thread.join(timeout=3)
                if self.thread.is_alive():
                    return
            try:
                self.metrics.shutdown()
            finally:
                self.store.cache.close()
        except Exception:
            # Collector cleanup is best effort and never exposes SDK/Redis details.
            return


def close_collector(collector: OTPMetricCollector | None) -> None:
    if collector is None:
        return
    try:
        collector.close()
    except Exception:
        # Even an injected collector's cleanup cannot take down local OTP service.
        return
