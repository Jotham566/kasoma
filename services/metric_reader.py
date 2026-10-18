"""Owned synchronous SDK delta reader; contains no exporter or network state."""

from opentelemetry.sdk.metrics import Counter, Histogram
from opentelemetry.sdk.metrics.export import AggregationTemporality, MetricReader, MetricsData


class DeltaReader(MetricReader):
    def __init__(self) -> None:
        super().__init__(
            preferred_temporality={
                Histogram: AggregationTemporality.DELTA,
                Counter: AggregationTemporality.DELTA,
            }
        )
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
