"""Local Redis cursor storage is disposable and scoped to an isolated synthetic schema."""

import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from redis import Redis

from services import export_cleanup_cursor as module
from services.export_cleanup import SweepResult
from services.export_storage import object_key, storage_scope

pytestmark = pytest.mark.integration


def test_actual_redis_cursor_has_ttl_and_overwrites_malformed_progress(content, monkeypatch):
    identity, *_ = content
    scope = storage_scope(identity.settings)
    cursor = object_key(uuid4(), uuid4(), scope=scope)
    key = "kasoma:exports:sweep:v1:" + scope
    seen = []

    def sweep(identity, store, **kwargs):
        seen.append(kwargs)
        return SweepResult(cursor=cursor, orphan_first=True)

    monkeypatch.setattr(module, "sweep", sweep)
    with Redis.from_url(
        identity.settings.redis_url.get_secret_value(),
        socket_connect_timeout=2,
        socket_timeout=2,
    ) as cache:
        owned = False
        try:
            # SET NX prevents replacing an unexpected pre-existing key, even in a test schema.
            owned = bool(cache.set(key, "malformed synthetic cursor", nx=True, ex=60))
            assert owned
            result = module.sweep_with_cursor(identity, SimpleNamespace(scope=scope), cache)
            assert result.failures == 1
            assert seen == [{"cursor": None, "orphan_first": False}]
            assert 0 < cache.ttl(key) <= 3600
            assert json.loads(cache.get(key)) == {"cursor": cursor, "orphan_first": True}
            assert (
                module.sweep_with_cursor(identity, SimpleNamespace(scope=scope), cache).failures
                == 0
            )
            assert seen[-1] == {"cursor": cursor, "orphan_first": True}
        finally:
            if owned:
                cache.delete(key)
