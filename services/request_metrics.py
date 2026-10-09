"""Closed, attribute-free OTel response-start histograms for local operations.

This component does not register a global provider or perform network I/O. The API
lifespan and bounded local exporter will own its reader and shutdown lifecycle.
"""

import json
from dataclasses import dataclass

from opentelemetry.sdk.metrics import AlwaysOffExemplarFilter, MeterProvider
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    Histogram,
    MetricReader,
    MetricsData,
)
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.sdk.resources import Resource

INSTRUMENT = "kasoma.api.response_start"
SCOPE = "kasoma.operations"
# Integer milliseconds, inclusive upper bounds; final bucket is unbounded.
BOUNDS_MS = (0, 10, 25, 50, 100, 250, 500, 1000, 1500, 3000, 8000, 30000)
MAX_COUNT = 2**53 - 1
MAX_INTERVAL_BYTES = 1024
MAX_TIME_NS = 2**63 - 1


@dataclass(frozen=True)
class HistogramEstimate:
    sample_size: int
    p95_lower_exclusive_ms: int | None
    p95_upper_inclusive_ms: int | None


def estimate(counts: tuple[int, ...]) -> HistogramEstimate:
    """Nearest-rank p95 interval, never a fabricated exact percentile.

    None/None with zero samples is empty. None/0 is a measured zero. A
    non-null lower bound with null upper bound is the overflow bucket.
    """
    if len(counts) != len(BOUNDS_MS) + 1 or any(
        type(value) is not int or value < 0 or value > MAX_COUNT for value in counts
    ):
        raise ValueError("INVALID_HISTOGRAM")
    total = sum(counts)
    if total > MAX_COUNT:
        raise ValueError("INVALID_HISTOGRAM")
    if not total:
        return HistogramEstimate(0, None, None)
    rank = (95 * total + 99) // 100
    cumulative = 0
    for index, count in enumerate(counts):
        cumulative += count
        if cumulative >= rank:
            return HistogramEstimate(
                total,
                BOUNDS_MS[index - 1] if index else None,
                BOUNDS_MS[index] if index < len(BOUNDS_MS) else None,
            )
    raise AssertionError("INVALID_HISTOGRAM")


@dataclass(frozen=True)
class HistogramInterval:
    start_ns: int
    end_ns: int
    counts: tuple[int, ...]

    def __post_init__(self) -> None:
        if (
            type(self.start_ns) is not int
            or type(self.end_ns) is not int
            or not 0 < self.start_ns <= self.end_ns <= MAX_TIME_NS
        ):
            raise ValueError("INVALID_METRIC_INTERVAL")
        estimate(self.counts)

    def encode(self) -> bytes:
        return json.dumps(
            {"v": 1, "start_ns": self.start_ns, "end_ns": self.end_ns, "counts": self.counts},
            separators=(",", ":"),
        ).encode("ascii")

    @classmethod
    def decode(cls, raw: bytes) -> "HistogramInterval":
        if len(raw) > MAX_INTERVAL_BYTES:
            raise ValueError("INVALID_METRIC_INTERVAL")
        try:
            value = json.loads(raw)
            if (
                not isinstance(value, dict)
                or set(value) != {"v", "start_ns", "end_ns", "counts"}
                or type(value["v"]) is not int
                or value["v"] != 1
                or not isinstance(value["counts"], list)
            ):
                raise ValueError
            result = cls(value["start_ns"], value["end_ns"], tuple(value["counts"]))
            # Only the canonical encoding is accepted, rejecting duplicate JSON keys
            # and alternate encodings before idempotency comparisons in storage.
            if raw != result.encode():
                raise ValueError
            return result
        except (ValueError, TypeError, UnicodeError, RecursionError):
            raise ValueError("INVALID_METRIC_INTERVAL") from None


def project(data: MetricsData) -> HistogramInterval | None:
    """Project only the one expected SDK series, dropping sums and all metadata.

    The caller handles missing collection freshness separately. Unexpected series,
    cumulative temporality or unsafe metadata fail closed rather than being stored.
    """
    if not data.resource_metrics:
        return None
    if len(data.resource_metrics) != 1:
        raise ValueError("INVALID_METRIC_BATCH")
    resource = data.resource_metrics[0]
    if (
        resource.resource.attributes != {"service.name": "kasoma-api"}
        or len(resource.scope_metrics) != 1
    ):
        raise ValueError("INVALID_METRIC_BATCH")
    scope = resource.scope_metrics[0]
    if scope.scope.name != SCOPE or scope.scope.version != "1" or len(scope.metrics) != 1:
        raise ValueError("INVALID_METRIC_BATCH")
    metric = scope.metrics[0]
    if (
        metric.name != INSTRUMENT
        or metric.unit != "ms"
        or not isinstance(metric.data, Histogram)
        or metric.data.aggregation_temporality != AggregationTemporality.DELTA
        or len(metric.data.data_points) != 1
    ):
        raise ValueError("INVALID_METRIC_BATCH")
    point = metric.data.data_points[0]
    if (
        point.attributes
        or point.exemplars
        or tuple(point.explicit_bounds) != BOUNDS_MS
        or type(point.count) is not int
        or point.count != sum(point.bucket_counts)
    ):
        raise ValueError("INVALID_METRIC_BATCH")
    return HistogramInterval(
        point.start_time_unix_nano, point.time_unix_nano, tuple(point.bucket_counts)
    )


class RequestMetrics:
    """One owned provider, one series, no arbitrary attribute or event input."""

    def __init__(self, reader: MetricReader) -> None:
        self.provider = MeterProvider(
            metric_readers=[reader],
            # Resource.create() also imports environment/host metadata. Do not use it.
            resource=Resource({"service.name": "kasoma-api"}),
            exemplar_filter=AlwaysOffExemplarFilter(),
            shutdown_on_exit=False,
            views=[
                View(
                    instrument_name=INSTRUMENT,
                    attribute_keys=set(),
                    aggregation=ExplicitBucketHistogramAggregation(
                        boundaries=BOUNDS_MS, record_min_max=False
                    ),
                )
            ],
        )
        self.histogram = self.provider.get_meter(SCOPE, "1").create_histogram(
            INSTRUMENT, unit="ms", description="API processing until response headers are ready"
        )

    def record(self, response_start_ms: int) -> None:
        if type(response_start_ms) is not int or not 0 <= response_start_ms <= MAX_COUNT:
            raise ValueError("INVALID_RESPONSE_START")
        self.histogram.record(response_start_ms)

    def shutdown(self) -> None:
        self.provider.shutdown(timeout_millis=2000)
