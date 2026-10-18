"""Finite Redis request-histogram codec; request wire format remains unchanged."""

from dataclasses import dataclass

from redis import Redis

from services.metric_interval_store import (
    CLOCK_SKEW_NS,
    BoundedIntervalStore,
)
from services.metric_interval_store import (
    MAX_INTERVALS as MAX_INTERVALS,
)
from services.metric_interval_store import (
    RETENTION_MS as RETENTION_MS,
)
from services.request_metrics import HistogramEstimate, HistogramInterval, estimate


@dataclass(frozen=True)
class RequestTimingSnapshot:
    estimate: HistogramEstimate
    interval_count: int
    capped: bool
    observed_start_ns: int | None
    observed_end_ns: int | None


class RequestMetricStore(BoundedIntervalStore):
    def __init__(self, cache: Redis, scope: str) -> None:
        super().__init__(cache, scope, kind="request")

    def read(self) -> RequestTimingSnapshot | None:
        try:
            batch = self.read_raw()
            if batch is None:
                return None
            intervals = [HistogramInterval.decode(value) for value in batch.payloads]
            if any(
                item.start_ns <= batch.now_ns - RETENTION_MS * 1_000_000
                or item.end_ns > batch.now_ns + CLOCK_SKEW_NS
                for item in intervals
            ):
                return None
            counts = tuple(sum(item.counts[i] for item in intervals) for i in range(13))
            return RequestTimingSnapshot(
                estimate(counts),
                len(intervals),
                batch.capped,
                min((item.start_ns for item in intervals), default=None),
                max((item.end_ns for item in intervals), default=None),
            )
        except Exception:
            return None
