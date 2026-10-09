"""Disposable progress cannot expand cleanup authority or retain state indefinitely."""

import json
from types import SimpleNamespace
from uuid import UUID

import pytest

from services import export_cleanup_cursor as module
from services.export_cleanup import SweepResult
from services.export_storage import object_key

SCOPE = "a" * 64
CURSOR = object_key(UUID(int=1), UUID(int=2), scope=SCOPE)


class Cache:
    def __init__(self, value=b"", *, read_failure=False, write_failure=False):
        self.value = value
        self.read_failure, self.write_failure = read_failure, write_failure
        self.saved = None

    def getrange(self, key, start, end):
        assert key == "kasoma:exports:sweep:v1:" + SCOPE
        assert (start, end) == (0, 512)
        if self.read_failure:
            raise RuntimeError("synthetic private provider diagnostic")
        return self.value

    def set(self, key, value, *, ex):
        self.saved = (key, json.loads(value), ex)
        if self.write_failure:
            raise RuntimeError("synthetic private provider diagnostic")
        return True


def install(monkeypatch, *, cursor=None, orphan_first=False):
    calls = []

    def fake_sweep(identity, storage, **kwargs):
        calls.append(kwargs)
        return SweepResult(removed=3, cursor=cursor, orphan_first=orphan_first)

    monkeypatch.setattr(module, "sweep", fake_sweep)
    return calls


def test_cursor_resumes_and_alternates_phases_with_finite_retention(monkeypatch):
    calls = install(monkeypatch, cursor=CURSOR, orphan_first=False)
    cache = Cache(json.dumps({"cursor": CURSOR, "orphan_first": True}).encode())
    result = module.sweep_with_cursor(None, SimpleNamespace(scope=SCOPE), cache)
    assert calls == [{"cursor": CURSOR, "orphan_first": True}]
    assert result.removed == 3 and result.failures == 0
    assert cache.saved == (
        "kasoma:exports:sweep:v1:" + SCOPE,
        {"cursor": CURSOR, "orphan_first": False},
        3600,
    )
    assert CURSOR not in repr(result)


@pytest.mark.parametrize(
    "raw",
    [
        b"x" * 513,
        b"not json",
        b"null",
        b"[]",
        b'{"cursor": null, "orphan_first": 1}',
        b'{"cursor": 7, "orphan_first": false}',
        b'{"cursor": null, "orphan_first": false, "authority": true}',
        json.dumps({"cursor": CURSOR.replace(SCOPE, "b" * 64), "orphan_first": True}).encode(),
    ],
)
def test_invalid_progress_restarts_without_granting_authority(monkeypatch, raw):
    calls = install(monkeypatch, orphan_first=True)
    cache = Cache(raw)
    result = module.sweep_with_cursor(None, SimpleNamespace(scope=SCOPE), cache)
    assert calls == [{"cursor": None, "orphan_first": False}]
    assert result.failures == 1 and result.removed == 3
    assert cache.saved[1] == {"cursor": None, "orphan_first": True}


def test_missing_or_expired_progress_starts_fresh(monkeypatch):
    calls = install(monkeypatch)
    result = module.sweep_with_cursor(None, SimpleNamespace(scope=SCOPE), Cache())
    assert calls == [{"cursor": None, "orphan_first": False}]
    assert result.failures == 0


def test_cache_outage_is_counted_and_does_not_block_authoritative_cleanup(monkeypatch):
    calls = install(monkeypatch)
    result = module.sweep_with_cursor(
        None, SimpleNamespace(scope=SCOPE), Cache(read_failure=True, write_failure=True)
    )
    assert len(calls) == 1
    assert result.removed == 3 and result.failures == 2
    assert "diagnostic" not in repr(result)


def test_invalid_namespace_never_reads_cache_or_sweeps(monkeypatch):
    calls = install(monkeypatch)
    with pytest.raises(ValueError, match="Invalid cleanup namespace"):
        module.sweep_with_cursor(None, SimpleNamespace(scope="foreign"), Cache())
    assert calls == []


def test_foreign_callback_cursor_is_not_persisted(monkeypatch):
    install(monkeypatch, cursor=CURSOR.replace(SCOPE, "b" * 64))
    cache = Cache()
    result = module.sweep_with_cursor(None, SimpleNamespace(scope=SCOPE), cache)
    assert result.failures == 1 and cache.saved is None
