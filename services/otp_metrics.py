"""Four fixed local OTP counters; no recipient, code, labels or network I/O."""

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
SCOPE = "kasoma.operations.otp"
RESOURCE = {"service.name": "kasoma-api-otp"}
NAMES = ("email_returned", "email_failed", "sms_returned", "sms_failed")
INSTRUMENTS = {"kasoma.otp." + name: "1" for name in NAMES}
Kind = Literal["EMAIL", "SMS"]
Outcome = Literal["RETURNED", "FAILED"]


def validate_counts(counts: tuple[int, ...]) -> None:
    if (
        type(counts) is not tuple
        or len(counts) != 4
        or any(type(value) is not int or not 0 <= value <= MAX_COUNT for value in counts)
    ):
        raise ValueError("INVALID_OTP_COUNTS")
    if sum(counts) > MAX_COUNT:
        raise ValueError("INCOHERENT_OTP_COUNTS")


@dataclass(frozen=True)
class OTPInterval:
    start_ns: int
    end_ns: int
    counts: tuple[int, ...]

    def __post_init__(self) -> None:
        if (
            type(self.start_ns) is not int
            or type(self.end_ns) is not int
            or not 0 < self.start_ns <= self.end_ns <= MAX_TIME_NS
        ):
            raise ValueError("INVALID_OTP_INTERVAL")
        validate_counts(self.counts)

    def encode(self) -> bytes:
        return json.dumps(
            {"v": 1, "start_ns": self.start_ns, "end_ns": self.end_ns, "counts": self.counts},
            separators=(",", ":"),
        ).encode("ascii")

    @classmethod
    def decode(cls, raw: bytes) -> "OTPInterval":
        if len(raw) > 1024:
            raise ValueError("INVALID_OTP_INTERVAL")
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
            raise ValueError("INVALID_OTP_INTERVAL") from None


def project(data: MetricsData | None, start_ns: int | None, observed: int) -> OTPInterval | None:
    if type(observed) is not int or not 0 <= observed <= MAX_COUNT:
        raise ValueError("INVALID_OTP_COLLECTION")
    if data is None or not data.resource_metrics:
        if observed:
            raise ValueError("MISSING_OTP_COLLECTION")
        return None
    if len(data.resource_metrics) != 1:
        raise ValueError("INVALID_OTP_RESOURCE")
    resource = data.resource_metrics[0]
    if resource.resource.attributes != RESOURCE:
        raise ValueError("INVALID_OTP_RESOURCE")
    if not resource.scope_metrics and observed == 0:
        return None
    if len(resource.scope_metrics) != 1:
        raise ValueError("INVALID_OTP_SCOPE")
    scope = resource.scope_metrics[0]
    if scope.scope.name != SCOPE or scope.scope.version != "1" or scope.scope.attributes:
        raise ValueError("INVALID_OTP_SCOPE")
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
            raise ValueError("INVALID_OTP_SERIES")
        point = metric.data.data_points[0]
        if (
            point.attributes
            or point.exemplars
            or type(point.value) is not int
            or not 0 <= point.value <= MAX_COUNT
            or not 0 < point.start_time_unix_nano <= point.time_unix_nano <= MAX_TIME_NS
        ):
            raise ValueError("INVALID_OTP_POINT")
        values[metric.name] = point.value
        ends.append(point.time_unix_nano)
    if observed == 0:
        if any(values.values()):
            raise ValueError("UNOWNED_OTP_OBSERVATION")
        return None
    if set(values) != set(INSTRUMENTS) or start_ns is None:
        raise ValueError("INCOMPLETE_OTP_COLLECTION")
    counts = tuple(values["kasoma.otp." + name] for name in NAMES)
    if sum(counts) != observed:
        raise ValueError("INCOHERENT_OTP_COLLECTION")
    return OTPInterval(start_ns, max(ends), counts)


class OTPMetrics:
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

    def record(self, kind: Kind, outcome: Outcome) -> None:
        if kind not in {"EMAIL", "SMS"} or outcome not in {"RETURNED", "FAILED"}:
            raise ValueError("INVALID_OTP_OUTCOME")
        target = f"{kind.lower()}_{outcome.lower()}"
        with self.lock:
            if self.closed or self.observed >= MAX_COUNT:
                return
            at = time_ns()
            self.start_ns = min(self.start_ns, at) if self.start_ns is not None else at
            self.observed += 1
            for name in NAMES:
                self.instruments["kasoma.otp." + name].add(int(name == target))

    def take(self, reader: DeltaReader) -> OTPInterval | None:
        # SDK collection contains only this owned provider's four synchronous series;
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
