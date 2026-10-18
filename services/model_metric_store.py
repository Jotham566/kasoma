"""Private five-minute model-counter window; no request or content metadata."""

from dataclasses import dataclass

from redis import Redis

from services.metric_interval_store import CLOCK_SKEW_NS, RETENTION_MS, BoundedIntervalStore
from services.model_metrics import ModelInterval, validate_counts


@dataclass(frozen=True)
class ModelUsageSnapshot:
    counts: tuple[int, ...]
    interval_count: int
    capped: bool
    observed_start_ns: int | None
    observed_end_ns: int | None


class ModelMetricStore(BoundedIntervalStore):
    def __init__(self, cache: Redis, scope: str) -> None:
        super().__init__(cache, scope, kind="model")

    def read(self) -> ModelUsageSnapshot | None:
        try:
            batch = self.read_raw()
            if batch is None:
                return None
            frames = [ModelInterval.decode(body) for body in batch.payloads]
            if any(
                frame.start_ns <= batch.now_ns - RETENTION_MS * 1_000_000
                or frame.end_ns > batch.now_ns + CLOCK_SKEW_NS
                for frame in frames
            ):
                return None
            counts = tuple(sum(frame.counts[index] for frame in frames) for index in range(6))
            validate_counts(counts)
            return ModelUsageSnapshot(
                counts,
                len(frames),
                batch.capped,
                min((frame.start_ns for frame in frames), default=None),
                max((frame.end_ns for frame in frames), default=None),
            )
        except Exception:
            return None
