"""Private five-minute OTP-counter window; no request or content metadata."""

from dataclasses import dataclass

from redis import Redis

from services.metric_interval_store import CLOCK_SKEW_NS, RETENTION_MS, BoundedIntervalStore
from services.otp_metrics import OTPInterval, validate_counts


@dataclass(frozen=True)
class OTPUsageSnapshot:
    counts: tuple[int, ...]
    interval_count: int
    capped: bool
    observed_start_ns: int | None
    observed_end_ns: int | None


class OTPMetricStore(BoundedIntervalStore):
    def __init__(self, cache: Redis, scope: str) -> None:
        super().__init__(cache, scope, kind="otp")

    def mark_loss(self, remaining_ms: int) -> None:
        if type(remaining_ms) is not int or not 1 <= remaining_ms <= RETENTION_MS:
            raise ValueError("INVALID_OTP_LOSS_WINDOW")
        # One finite marker for the aggregate namespace; never shorten another
        # producer's uncertainty window. READ checks it atomically before data.
        self.cache.eval(
            """
          local ttl = redis.call('PTTL', KEYS[1])
          if ttl < tonumber(ARGV[1]) then
            redis.call('SET', KEYS[1], '1', 'PX', ARGV[1])
          end
          return 1
        """,
            1,
            self.prefix + "incomplete",
            remaining_ms,
        )

    def read(self) -> OTPUsageSnapshot | None:
        try:
            batch = self.read_raw()
            if batch is None:
                return None
            frames = [OTPInterval.decode(body) for body in batch.payloads]
            if any(
                frame.start_ns <= batch.now_ns - RETENTION_MS * 1_000_000
                or frame.end_ns > batch.now_ns + CLOCK_SKEW_NS
                for frame in frames
            ):
                return None
            counts = tuple(sum(frame.counts[index] for frame in frames) for index in range(4))
            validate_counts(counts)
            return OTPUsageSnapshot(
                counts,
                len(frames),
                batch.capped,
                min((frame.start_ns for frame in frames), default=None),
                max((frame.end_ns for frame in frames), default=None),
            )
        except Exception:
            return None
