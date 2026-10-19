"""Shared bounded byte transport; concrete codecs own metric semantics and privacy."""

import hashlib
import re
from dataclasses import dataclass
from typing import Literal, Protocol, cast
from uuid import UUID

from redis import Redis

RETENTION_MS = 300_000
MAX_INTERVALS = 256
FRESH_MS = 15_000
CLOCK_SKEW_NS = 1_000_000_000

# Only this namespace's registry and interval keys are touched. Individual absolute
# expiries prevent retries or another producer's activity extending data retention.
WRITE = """
local now = redis.call('TIME')
local ms = tonumber(now[1]) * 1000 + math.floor(tonumber(now[2]) / 1000)
local expiry = tonumber(ARGV[2])
local ended = tonumber(ARGV[3])
if expiry <= ms or expiry > ms + 301000 or ended > ms + 1000 then return 0 end
expiry = math.min(expiry, ms + 300000)
if redis.call('ZCARD', KEYS[1]) > 256 then return -1 end
local expired = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ms)
for _, member in ipairs(expired) do redis.call('ZREM', KEYS[1], member) end
if redis.call('STRLEN', KEYS[2]) > 1024 then return -1 end
local previous = redis.call('GET', KEYS[2])
if previous and previous ~= ARGV[1] then return -1 end
if not previous then
    redis.call('SET', KEYS[2], ARGV[1], 'PXAT', expiry)
    redis.call('ZADD', KEYS[1], expiry, ARGV[4])
end
if redis.call('ZCARD', KEYS[1]) > 256 then
    local oldest = redis.call('ZRANGE', KEYS[1], 0, 0)
    redis.call('ZREM', KEYS[1], oldest[1])
    -- Members are opaque fixed-length hashes, never arbitrary Redis key names.
    if string.len(oldest[1]) ~= 64 or string.find(oldest[1], '[^0-9a-f]') then return -1 end
    redis.call('DEL', ARGV[5] .. oldest[1])
    redis.call('SET', KEYS[3], '1', 'PX', 300000)
end
redis.call('PEXPIRE', KEYS[1], 300000)
redis.call('SET', KEYS[4], tostring(ms), 'PX', 15000)
return 1
"""

READ = """
if #KEYS == 4 and redis.call('EXISTS', KEYS[4]) == 1 then return {} end
local now = redis.call('TIME')
local ms = tonumber(now[1]) * 1000 + math.floor(tonumber(now[2]) / 1000)
if redis.call('ZCARD', KEYS[1]) > 256 then return {} end
if redis.call('STRLEN', KEYS[3]) > 16 or redis.call('STRLEN', KEYS[2]) > 1 then return {} end
local fresh = redis.call('GET', KEYS[3])
if not fresh or string.len(fresh) > 16 then return {} end
local at = tonumber(fresh)
if not at or at > ms or ms - at >= 15000 then return {} end
local members = redis.call('ZRANGEBYSCORE', KEYS[1], '(' .. ms, '+inf')
local capped = redis.call('GET', KEYS[2])
if capped and capped ~= '1' then return {} end
local result = {now[1] .. string.format('%06d', tonumber(now[2])), capped or '0'}
for _, member in ipairs(members) do
    if string.len(member) ~= 64 or string.find(member, '[^0-9a-f]') then return {} end
    local key = ARGV[1] .. member
    if redis.call('STRLEN', key) > 1024 then return {} end
    local body = redis.call('GET', key)
    -- A missing unexpired entry is lost data, not a measured empty interval.
    if not body then return {} end
    table.insert(result, body)
end
return result
"""

PULSE = """
local now = redis.call('TIME')
local ms = tonumber(now[1]) * 1000 + math.floor(tonumber(now[2]) / 1000)
redis.call('SET', KEYS[1], tostring(ms), 'PX', 15000)
return 1
"""


class EncodedInterval(Protocol):
    @property
    def start_ns(self) -> int: ...

    @property
    def end_ns(self) -> int: ...

    def encode(self) -> bytes: ...


@dataclass(frozen=True)
class RawIntervalBatch:
    now_ns: int
    capped: bool
    payloads: tuple[bytes, ...]


class BoundedIntervalStore:
    def __init__(
        self, cache: Redis, scope: str, *, kind: Literal["request", "model", "otp"]
    ) -> None:
        if re.fullmatch(r"[0-9a-f]{64}", scope) is None or kind not in {"request", "model", "otp"}:
            raise ValueError("INVALID_METRIC_SCOPE")
        self.cache = cache
        self.kind = kind
        self.prefix = f"kasoma:ops:{kind}:" + scope + ":"
        self.registry = self.prefix + "intervals"
        self.capped = self.prefix + "capped"
        self.fresh = self.prefix + "fresh"
        self.data_prefix = self.prefix + "data:"

    def interval_key(self, source: UUID, interval: EncodedInterval) -> str:
        # A random per-process source prevents collision between independent readers;
        # it is not a machine, request or learner identifier and is never displayed.
        token = hashlib.sha256(
            f"{source.hex}:{interval.start_ns}:{interval.end_ns}".encode("ascii")
        ).hexdigest()
        return self.data_prefix + token

    def write(self, source: UUID, interval: EncodedInterval) -> bool:
        key = self.interval_key(source, interval)
        # Expire relative to the earliest possible observation, not export/retry time.
        expiry = interval.start_ns // 1_000_000 + RETENTION_MS
        content = interval.encode()
        if not isinstance(content, bytes) or len(content) > 1024:
            raise ValueError("INVALID_METRIC_INTERVAL")
        result = cast(
            object,
            self.cache.eval(
                WRITE,
                4,
                self.registry,
                key,
                self.capped,
                self.fresh,
                content,
                expiry,
                interval.end_ns // 1_000_000,
                key.removeprefix(self.data_prefix),
                self.data_prefix,
            ),
        )
        if result == -1:
            raise ValueError("INVALID_METRIC_STORE")
        return result == 1

    def pulse(self) -> None:
        """Called only after a successful SDK collection, including an empty one."""
        self.cache.eval(PULSE, 1, self.fresh)

    def mark_loss(self, remaining_ms: int) -> None:
        if type(remaining_ms) is not int or not 1 <= remaining_ms <= RETENTION_MS:
            raise ValueError("INVALID_METRIC_LOSS_WINDOW")
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

    def read_raw(self) -> RawIntervalBatch | None:
        try:
            keys = [self.registry, self.capped, self.fresh]
            keys.append(self.prefix + "incomplete")
            raw = self.cache.eval(READ, len(keys), *keys, self.data_prefix)
            if not isinstance(raw, list) or not 2 <= len(raw) <= MAX_INTERVALS + 2:
                return None
            now_ns = int(raw[0]) * 1000
            if not 0 < now_ns <= 2**63 - 1 or raw[1] not in (b"0", b"1"):
                return None
            if any(not isinstance(body, bytes) or len(body) > 1024 for body in raw[2:]):
                return None
            return RawIntervalBatch(now_ns, raw[1] == b"1", tuple(raw[2:]))
        except Exception:
            # Redis exceptions may contain credentials or payloads; never log them.
            return None
