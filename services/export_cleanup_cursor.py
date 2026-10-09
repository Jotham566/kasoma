"""Disposable ADR-048 sweep progress; never a source of deletion authority."""

import json
import re
from typing import Protocol

from services.export_cleanup import CleanupStore, SweepResult, sweep
from services.export_storage import parse_key
from services.identity import IdentityService

MAX_STATE_BYTES = 512
CURSOR_TTL_SECONDS = 3600


class CursorCache(Protocol):
    def getrange(self, name: str, start: int, end: int) -> object: ...

    def set(self, name: str, value: str, *, ex: int) -> object: ...


def sweep_with_cursor(
    identity: IdentityService, storage: CleanupStore, cache: CursorCache
) -> SweepResult:
    if re.fullmatch(r"[a-f0-9]{64}", storage.scope) is None:
        raise ValueError("Invalid cleanup namespace")
    key = "kasoma:exports:sweep:v1:" + storage.scope
    cursor, orphan_first = None, False
    failures = 0
    try:
        # A corrupt cache entry cannot cause an unbounded read or JSON allocation.
        raw = cache.getrange(key, 0, MAX_STATE_BYTES)
        if raw != b"":
            if type(raw) is not bytes or len(raw) > MAX_STATE_BYTES:
                raise ValueError("Invalid sweep state")
            state = json.loads(raw)
            if (
                type(state) is not dict
                or set(state) != {"cursor", "orphan_first"}
                or type(state["orphan_first"]) is not bool
            ):
                raise ValueError("Invalid sweep state")
            candidate = state["cursor"]
            if candidate is not None:
                if type(candidate) is not str:
                    raise ValueError("Invalid sweep cursor")
                parse_key(candidate, scope=storage.scope)
            cursor, orphan_first = candidate, state["orphan_first"]
    except Exception:
        # Lost/malformed progress safely restarts the bounded scan. SQL remains authoritative.
        failures += 1
    result = sweep(identity, storage, cursor=cursor, orphan_first=orphan_first)
    try:
        if result.cursor is not None:
            parse_key(result.cursor, scope=storage.scope)
        value = json.dumps({"cursor": result.cursor, "orphan_first": result.orphan_first})
        if len(value.encode()) > MAX_STATE_BYTES:
            raise ValueError("Invalid sweep state")
        if not cache.set(key, value, ex=CURSOR_TTL_SECONDS):
            raise ValueError("Sweep state not saved")
    except Exception:
        failures += 1
    result.failures += failures
    return result
