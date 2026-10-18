"""Six fixed local gateway counters; no content, labels, identifiers or network I/O."""

import json
from dataclasses import dataclass
from threading import Lock
from time import time_ns
from typing import Literal

from opentelemetry.sdk.metrics import AlwaysOffExemplarFilter, MeterProvider
from opentelemetry.sdk.metrics.export import AggregationTemporality, MetricReader, MetricsData, Sum
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource

from services.metric_reader import DeltaReader

MAX_COUNT = 2**53 - 1
MAX_TIME_NS = 2**63 - 1
SCOPE = "kasoma.operations.model"
RESOURCE = {"service.name": "kasoma-worker-model"}
# candidate, fallback, unavailable result, unavailable usage, known input, known output
NAMES = ("candidates", "fallbacks", "unavailable", "usage_unknown", "input_tokens", "output_tokens")
INSTRUMENTS = {
    "kasoma.model." + name: "tokens" if name.endswith("tokens") else "1" for name in NAMES
}
Outcome = Literal["CANDIDATE", "LOW_CONFIDENCE", "UNAVAILABLE"]


def validate_counts(counts: tuple[int, ...]) -> None:
    if (
        type(counts) is not tuple
        or len(counts) != 6
        or any(type(value) is not int or not 0 <= value <= MAX_COUNT for value in counts)
    ):
        raise ValueError("INVALID_MODEL_COUNTS")
    candidates, fallbacks, unavailable, unknown, incoming, outgoing = counts
    total = candidates + fallbacks + unavailable
    if (
        total > MAX_COUNT
        or not unavailable <= unknown <= total
        or incoming > (total - unknown) * 8192
        or outgoing > (total - unknown) * 4096
    ):
        raise ValueError("INCOHERENT_MODEL_COUNTS")


@dataclass(frozen=True)
class ModelInterval:
    start_ns: int
    end_ns: int
    counts: tuple[int, ...]

    def __post_init__(self) -> None:
        if (
            type(self.start_ns) is not int
            or type(self.end_ns) is not int
            or not 0 < self.start_ns <= self.end_ns <= MAX_TIME_NS
        ):
            raise ValueError("INVALID_MODEL_INTERVAL")
        validate_counts(self.counts)

    def encode(self) -> bytes:
        return json.dumps(
            {"v": 1, "start_ns": self.start_ns, "end_ns": self.end_ns, "counts": self.counts},
            separators=(",", ":"),
        ).encode("ascii")

    @classmethod
    def decode(cls, raw: bytes) -> "ModelInterval":
        if len(raw) > 1024:
            raise ValueError("INVALID_MODEL_INTERVAL")
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
            if raw != result.encode():
                raise ValueError
            return result
        except (ValueError, TypeError, UnicodeError, RecursionError):
            raise ValueError("INVALID_MODEL_INTERVAL") from None


def project(data: MetricsData | None, start_ns: int | None, observed: int) -> ModelInterval | None:
    if type(observed) is not int or not 0 <= observed <= MAX_COUNT:
        raise ValueError("INVALID_MODEL_COLLECTION")
    if data is None or not data.resource_metrics:
        if observed:
            raise ValueError("MISSING_MODEL_COLLECTION")
        return None
    if len(data.resource_metrics) != 1:
        raise ValueError("INVALID_MODEL_RESOURCE")
    resource = data.resource_metrics[0]
    if resource.resource.attributes != RESOURCE:
        raise ValueError("INVALID_MODEL_RESOURCE")
    if not resource.scope_metrics and observed == 0:
        return None
    if len(resource.scope_metrics) != 1:
        raise ValueError("INVALID_MODEL_SCOPE")
    scope = resource.scope_metrics[0]
    if scope.scope.name != SCOPE or scope.scope.version != "1" or scope.scope.attributes:
        raise ValueError("INVALID_MODEL_SCOPE")
    values: dict[str, int] = {}
    ends: list[int] = []
    for metric in scope.metrics:
        if (
            metric.name not in INSTRUMENTS
            or metric.name in values
            or metric.unit != INSTRUMENTS[metric.name]
            or not isinstance(metric.data, Sum)
            or metric.data.aggregation_temporality != AggregationTemporality.DELTA
            or not metric.data.is_monotonic
            or len(metric.data.data_points) != 1
        ):
            raise ValueError("INVALID_MODEL_SERIES")
        point = metric.data.data_points[0]
        if (
            point.attributes
            or point.exemplars
            or type(point.value) is not int
            or not 0 <= point.value <= MAX_COUNT
            or not 0 < point.start_time_unix_nano <= point.time_unix_nano <= MAX_TIME_NS
        ):
            raise ValueError("INVALID_MODEL_POINT")
        values[metric.name] = point.value
        ends.append(point.time_unix_nano)
    if observed == 0:
        if any(values.values()):
            raise ValueError("UNOWNED_MODEL_OBSERVATION")
        return None
    if set(values) != set(INSTRUMENTS) or start_ns is None:
        raise ValueError("INCOMPLETE_MODEL_COLLECTION")
    counts = tuple(values["kasoma.model." + name] for name in NAMES)
    if sum(counts[:3]) != observed:
        raise ValueError("INCOHERENT_MODEL_COLLECTION")
    return ModelInterval(start_ns, max(ends), counts)


class ModelMetrics:
    def __init__(self, reader: MetricReader) -> None:
        self.lock = Lock()
        self.start_ns: int | None = None
        self.observed = 0
        self.closed = False
        self.provider = MeterProvider(
            metric_readers=[reader],
            resource=Resource(RESOURCE),
            exemplar_filter=AlwaysOffExemplarFilter(),
            shutdown_on_exit=False,
            views=[View(instrument_name=name, attribute_keys=set()) for name in INSTRUMENTS],
        )
        meter = self.provider.get_meter(SCOPE, "1")
        self.instruments = {
            name: meter.create_counter(name, unit=unit) for name, unit in INSTRUMENTS.items()
        }

    def record(self, outcome: Outcome, incoming: int | None, outgoing: int | None) -> None:
        if outcome not in {"CANDIDATE", "LOW_CONFIDENCE", "UNAVAILABLE"}:
            raise ValueError("INVALID_MODEL_OUTCOME")
        known = incoming is not None and outgoing is not None
        if (incoming is None) != (outgoing is None):
            raise ValueError("INCOMPLETE_MODEL_USAGE")
        if known and (
            type(incoming) is not int
            or type(outgoing) is not int
            or not 0 <= incoming <= 8192
            or not 0 <= outgoing <= 4096
        ):
            raise ValueError("INVALID_MODEL_USAGE")
        if outcome == "UNAVAILABLE" and known:
            raise ValueError("UNAVAILABLE_MODEL_USAGE")
        increments = (
            int(outcome == "CANDIDATE"),
            int(outcome == "LOW_CONFIDENCE"),
            int(outcome == "UNAVAILABLE"),
            int(not known),
            incoming or 0,
            outgoing or 0,
        )
        with self.lock:
            if self.closed or self.observed >= MAX_COUNT:
                return
            at = time_ns()
            self.start_ns = min(self.start_ns, at) if self.start_ns is not None else at
            self.observed += 1
            for name, value in zip(NAMES, increments, strict=True):
                self.instruments["kasoma.model." + name].add(value)

    def take(self, reader: DeltaReader) -> ModelInterval | None:
        # SDK collection contains only this owned provider's six synchronous series;
        # no callbacks/Redis work run under this short record/collection lock.
        with self.lock:
            data = reader.take()
            start, observed = self.start_ns, self.observed
            self.start_ns, self.observed = None, 0
        return project(data, start, observed)

    def shutdown(self) -> None:
        with self.lock:
            self.closed = True
            self.provider.shutdown(timeout_millis=2000)


_active: ModelMetrics | None = None


def activate(metrics: ModelMetrics | None) -> None:
    global _active
    _active = metrics


def observe(outcome: Outcome, incoming: int | None, outgoing: int | None) -> None:
    try:
        if _active is not None:
            _active.record(outcome, incoming, outgoing)
    except Exception:
        # Metrics are best effort; never leak data or change a provider outcome.
        return
