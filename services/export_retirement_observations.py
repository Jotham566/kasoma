"""Five-minute, dataset-scoped count-only observations; never deletion authority."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import Field
from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry

from services.identity_contracts import Contract

WRITE = """
local seconds=tonumber(redis.call('TIME')[1])
local value=cjson.decode(ARGV[1])
value.observed_at=seconds
redis.call('SET',KEYS[1]..':last',cjson.encode(value),'EX',300)
if value.status=='FAILED' then
  local key=KEYS[1]..':fail:'..math.floor(seconds/300)
  if tonumber(redis.call('GET',key) or '0')<10001 then redis.call('INCR',key) end
  redis.call('EXPIREAT',key,(math.floor(seconds/300)+1)*300)
end
return 1
"""
READ = """
local seconds=tonumber(redis.call('TIME')[1])
return {redis.call('GET',KEYS[1]..':last') or '',
  redis.call('GET',KEYS[1]..':fail:'..math.floor(seconds/300)) or '0',seconds}
"""


class Observation(Contract):
    status: Literal["PROCESSED", "DISABLED", "BUSY", "FAILED"]
    removed: int = Field(default=0, ge=0, le=100)
    examined: int = Field(default=0, ge=0, le=200)
    exhausted: bool = False
    observed_at: int = Field(default=0, ge=0, le=2**53 - 1)


def key(database: str, namespace: str) -> str:
    # Operational dataset names, not learner identifiers or a new answer fingerprint.
    scope = json.dumps([database, namespace], separators=(",", ":"))
    return "kasoma:retirement:" + hashlib.sha256(scope.encode()).hexdigest()


def connection(url: str) -> Redis:
    return Redis.from_url(
        url,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
        max_connections=1,
        retry=Retry(NoBackoff(), 0),
    )


def record(url: str, scope: tuple[str, str], value: Observation) -> bool:
    try:
        with connection(url) as cache:
            return bool(cache.eval(WRITE, 1, key(*scope), value.model_dump_json()) == 1)
    except Exception:
        return False


def read(url: str, scope: tuple[str, str]) -> tuple[Observation | None, int] | None:
    try:
        with connection(url) as cache:
            raw = cache.eval(READ, 1, key(*scope))
        if (
            not isinstance(raw, list)
            or len(raw) != 3
            or not isinstance(raw[0], bytes)
            or len(raw[0]) > 1024
        ):
            return None
        failures, now = int(raw[1]), int(raw[2])
        if not 0 <= failures <= 10001:
            return None
        value = Observation.model_validate_json(raw[0]) if raw[0] else None
        if value is not None and not 0 <= now - value.observed_at < 300:
            return None
        return value, failures
    except Exception:
        return None


def timestamp(value: Observation) -> datetime:
    return datetime.fromtimestamp(value.observed_at, UTC)
