"""Real SDK aggregation with in-memory readers; no external telemetry calls."""

import json
from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import strategies as st
from opentelemetry.sdk.metrics import Histogram
from opentelemetry.sdk.metrics.export import AggregationTemporality, InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider

from services.request_metrics import (
    BOUNDS_MS,
    MAX_COUNT,
    HistogramInterval,
    RequestMetrics,
    estimate,
    project,
)


def test_sdk_delta_buckets_minimize_resource_and_trace_context(monkeypatch):
    monkeypatch.setenv("OTEL_RESOURCE_ATTRIBUTES", "learner=CANARY-private")
    monkeypatch.setenv("OTEL_SERVICE_NAME", "CANARY-private")
    reader = InMemoryMetricReader(preferred_temporality={Histogram: AggregationTemporality.DELTA})
    metrics = RequestMetrics(reader)
    traces = TracerProvider()
    try:
        with traces.get_tracer("test").start_as_current_span("CANARY-private"):
            for value in (0, 10, 11, 500, 30001):
                metrics.record(value)
        data = reader.get_metrics_data()
        assert data is not None
        assert "CANARY" not in data.to_json()
        assert data.resource_metrics[0].resource.attributes == {"service.name": "kasoma-api"}
        metric = data.resource_metrics[0].scope_metrics[0].metrics[0]
        assert metric.data.aggregation_temporality == AggregationTemporality.DELTA
        point = metric.data.data_points[0]
        assert point.attributes == {}
        assert point.exemplars == []
        assert point.explicit_bounds == BOUNDS_MS
        assert point.count == 5
        assert point.bucket_counts == (1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
        interval = project(data)
        assert interval is not None
        assert HistogramInterval.decode(interval.encode()) == interval
        assert set(json.loads(interval.encode())) == {"v", "start_ns", "end_ns", "counts"}
        assert len(interval.encode()) <= 1024
        assert interval.counts == point.bucket_counts
        # SDK represents disabled extrema as infinities; the future storage projection
        # must take only bounds/counts/timestamps, never blindly serialize SDK JSON.
        metrics.record(25)
        second = reader.get_metrics_data().resource_metrics[0].scope_metrics[0].metrics[0]
        assert second.data.data_points[0].count == 1
        assert second.data.data_points[0].bucket_counts[2] == 1
        assert json.loads(data.to_json())["resource_metrics"]
    finally:
        metrics.shutdown()
        traces.shutdown()


def test_empty_zero_and_overflow_are_distinct():
    empty = estimate((0,) * 13)
    zero = estimate((1,) + (0,) * 12)
    overflow = estimate((0,) * 12 + (1,))
    assert empty.sample_size == 0
    assert empty.p95_upper_inclusive_ms is None
    assert zero.sample_size == 1 and zero.p95_upper_inclusive_ms == 0
    assert overflow.p95_lower_exclusive_ms == 30000
    assert overflow.p95_upper_inclusive_ms is None


@given(st.lists(st.integers(min_value=0, max_value=100000), min_size=1, max_size=300))
def test_histogram_interval_contains_exact_nearest_rank(values):
    counts = [0] * 13
    for value in values:
        bucket = next((i for i, bound in enumerate(BOUNDS_MS) if value <= bound), 12)
        counts[bucket] += 1
    result = estimate(tuple(counts))
    exact = sorted(values)[(95 * len(values) + 99) // 100 - 1]
    assert result.sample_size == len(values)
    assert result.p95_lower_exclusive_ms is None or exact > result.p95_lower_exclusive_ms
    assert result.p95_upper_inclusive_ms is None or exact <= result.p95_upper_inclusive_ms


@pytest.mark.parametrize(
    "counts", [(), (0,) * 12, (-1,) * 13, (True,) * 13, (1.5,) * 13, (MAX_COUNT,) * 13]
)
def test_malformed_histograms_fail_closed(counts):
    with pytest.raises(ValueError, match="^INVALID_HISTOGRAM$"):
        estimate(counts)


@pytest.mark.parametrize("value", [-1, True, 1.5, float("nan"), float("inf"), MAX_COUNT + 1])
def test_measurement_rejects_non_integer_or_unbounded_input(value):
    metrics = RequestMetrics(InMemoryMetricReader())
    try:
        with pytest.raises(ValueError, match="^INVALID_RESPONSE_START$"):
            metrics.record(value)
    finally:
        metrics.shutdown()


@pytest.mark.parametrize(
    "raw",
    [b"{}", b"[]", b"null", b"\xff", b"x" * 1025, b"[" * 1000, b'{"v":true}', b'{"v":1,"v":1}'],
)
def test_untrusted_interval_bytes_have_closed_failure(raw):
    with pytest.raises(ValueError, match="^INVALID_METRIC_INTERVAL$"):
        HistogramInterval.decode(raw)


def test_canonical_interval_rejects_duplicate_keys_and_injected_fields():
    raw = HistogramInterval(1, 2, (1,) + (0,) * 12).encode()
    for corrupt in (
        raw.replace(b'"v":1', b'"v":1,"v":1'),
        raw.replace(b'"v":1', b'"v":1,"learner":"CANARY-private"'),
        raw.replace(b'"end_ns":2', b'"end_ns":0'),
        raw.replace(b'"start_ns":1', b'"start_ns":true'),
    ):
        with pytest.raises(ValueError, match="^INVALID_METRIC_INTERVAL$"):
            HistogramInterval.decode(corrupt)


def test_projection_rejects_cumulative_and_unexpected_sdk_series():
    reader = InMemoryMetricReader()
    metrics = RequestMetrics(reader)
    try:
        metrics.record(10)
        data = reader.get_metrics_data()
        with pytest.raises(ValueError, match="^INVALID_METRIC_BATCH$"):
            project(data)
    finally:
        metrics.shutdown()
    reader = InMemoryMetricReader(preferred_temporality={Histogram: AggregationTemporality.DELTA})
    metrics = RequestMetrics(reader)
    try:
        metrics.record(10)
        data = reader.get_metrics_data()
        resource = data.resource_metrics[0]
        scope = resource.scope_metrics[0]
        metric = scope.metrics[0]
        point = metric.data.data_points[0]
        for changed in (
            replace(point, count=2),
            replace(point, attributes={"x": "CANARY"}),
            replace(point, explicit_bounds=(1,)),
            replace(point, count=True),
        ):
            changed_metric = replace(metric, data=replace(metric.data, data_points=[changed]))
            altered = replace(
                data,
                resource_metrics=[
                    replace(resource, scope_metrics=[replace(scope, metrics=[changed_metric])])
                ],
            )
            with pytest.raises(ValueError, match="^INVALID_METRIC_BATCH$"):
                project(altered)
    finally:
        metrics.shutdown()
