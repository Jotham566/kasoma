"""No-network object adapter checks, including bounded reads and response cleanup."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from services import export_storage as storage
from services.export_artifacts import MAX_CIPHERTEXT_BYTES, ArtifactError


class Response:
    def __init__(self, value=b"synthetic ciphertext", length=None, failure=None):
        self.value, self.failure = value, failure
        self.headers = {"Content-Length": length if length is not None else str(len(value))}
        self.reads, self.closed, self.released = [], 0, 0

    def read(self, size):
        self.reads.append(size)
        if self.failure == "read":
            raise RuntimeError("synthetic confidential response")
        return self.value[:size]

    def close(self):
        self.closed += 1
        if self.failure == "close":
            raise RuntimeError("synthetic confidential close")

    def release_conn(self):
        self.released += 1
        if self.failure == "release":
            raise RuntimeError("synthetic confidential release")


class Client:
    def __init__(self):
        self.response = Response()
        self.calls = []

    def get_object(self, container, key):
        self.calls.append(("get", container, key))
        return self.response

    def put_object(self, container, key, stream, size, *, content_type):
        self.calls.append(("put", container, key, stream.read(size + 1), size, content_type))
        self.stream = stream

    def remove_object(self, container, key):
        self.calls.append(("remove", container, key))


@pytest.fixture
def adapter(monkeypatch, settings):
    client = Client()
    monkeypatch.setattr(
        storage,
        "MinioObjectStorage",
        lambda _: SimpleNamespace(client=client, container="synthetic"),
    )
    return storage.PrivateExportStorage(settings), client, uuid4(), uuid4()


def test_private_keys_and_bounded_round_trip(adapter):
    obj, client, generation, target = adapter
    raw = b"x" * MAX_CIPHERTEXT_BYTES
    obj.put(generation, target, raw)
    assert client.stream.closed
    assert client.calls == [
        (
            "put",
            "synthetic",
            f"private-exports/v1/{obj.scope}/{generation}/{target}",
            raw,
            len(raw),
            "application/octet-stream",
        )
    ]
    client.response = Response(raw)
    assert obj.get(generation, target) == raw
    assert client.response.reads == [MAX_CIPHERTEXT_BYTES + 1]
    assert client.response.closed == client.response.released == 1
    obj.remove(generation, target)
    assert client.calls[-1] == (
        "remove",
        "synthetic",
        f"private-exports/v1/{obj.scope}/{generation}/{target}",
    )


@pytest.mark.parametrize(
    "length", ["", "-1", "0", "131073", "9999999", "１２", "12.0", " 12", "12 "]
)
def test_bad_content_length_never_reads_body_and_always_closes(adapter, length):
    obj, client, generation, target = adapter
    client.response = Response(length=length)
    with pytest.raises(ArtifactError, match="READ_FAILED"):
        obj.get(generation, target)
    assert client.response.reads == []
    assert client.response.closed == client.response.released == 1


@pytest.mark.parametrize("failure", ["read", "close", "release"])
def test_response_failures_do_not_leak_and_release_connections(adapter, failure):
    obj, client, generation, target = adapter
    client.response = Response(failure=failure)
    with pytest.raises(ArtifactError) as exc:
        obj.get(generation, target)
    assert str(exc.value) == "EXPORT_OBJECT_READ_FAILED"
    assert exc.value.__suppress_context__
    assert client.response.closed == client.response.released == 1


@pytest.mark.parametrize("value", [b"x", b"x" * 11])
def test_truncated_or_overlong_response_is_not_accepted(adapter, value):
    obj, client, generation, target = adapter
    client.response = Response(value, length="10")
    with pytest.raises(ArtifactError, match="READ_FAILED"):
        obj.get(generation, target)
    assert client.response.reads == [11]
    assert client.response.closed == client.response.released == 1


@pytest.mark.parametrize("value", [b"", b"x" * (MAX_CIPHERTEXT_BYTES + 1), "text"])
def test_write_bounds_before_storage(adapter, value):
    obj, client, generation, target = adapter
    with pytest.raises(ArtifactError, match="WRITE_FAILED"):
        obj.put(generation, target, value)
    assert not client.calls


@pytest.mark.parametrize("operation", ["put", "get", "remove"])
def test_non_uuid_references_cannot_escape_owned_prefix(adapter, operation):
    obj, client, _, target = adapter
    args = ["../../unrelated", target] + ([b"x"] if operation == "put" else [])
    with pytest.raises(ArtifactError, match="INVALID"):
        getattr(obj, operation)(*args)
    assert not client.calls


@pytest.mark.parametrize(
    "operation,method", [("put", "put_object"), ("get", "get_object"), ("remove", "remove_object")]
)
def test_provider_diagnostics_are_never_returned(adapter, monkeypatch, operation, method):
    obj, client, generation, target = adapter

    streams = []

    def failure(*args, **kwargs):
        if operation == "put":
            streams.append(args[2])
        raise RuntimeError("synthetic secret URL/credential/provider diagnostics")

    monkeypatch.setattr(client, method, failure)
    args = [generation, target] + ([b"x"] if operation == "put" else [])
    with pytest.raises(ArtifactError) as exc:
        getattr(obj, operation)(*args)
    assert "synthetic" not in str(exc.value)
    assert exc.value.__suppress_context__
    if operation == "put":
        # BytesIO is a context manager even when the provider rejects the write.
        assert not client.calls
        assert len(streams) == 1 and streams[0].closed


def test_listing_is_bounded_scoped_and_closes_generator(adapter, monkeypatch):
    from datetime import UTC, datetime
    from uuid import UUID

    obj, client, generation, _ = adapter
    calls, closed = [], []

    def listing(container, **options):
        calls.append((container, options))
        try:
            for number in [1, 2]:
                yield SimpleNamespace(
                    object_name=storage.object_key(generation, UUID(int=number), scope=obj.scope),
                    last_modified=datetime(2026, 9, 23, tzinfo=UTC),
                )
            raise AssertionError("Bounded page must not request a third item")
        finally:
            closed.append(True)

    monkeypatch.setattr(client, "list_objects", listing, raising=False)
    after = storage.object_key(generation, UUID(int=0), scope=obj.scope)
    page = obj.page(generation=generation, after=after, limit=2)
    assert [value.object_id.int for value in page] == [1, 2]
    assert closed == [True]
    assert calls == [
        (
            "synthetic",
            {
                "prefix": f"private-exports/v1/{obj.scope}/{generation}/",
                "recursive": True,
                "start_after": after,
            },
        )
    ]


@pytest.mark.parametrize("bad", ["key", "scope", "time", "order"])
def test_listing_rejects_malformed_scope_time_or_order(adapter, monkeypatch, bad):
    from datetime import UTC, datetime

    obj, client, generation, target = adapter
    at = datetime(2026, 9, 23, tzinfo=UTC)
    key = storage.object_key(generation, target, scope=obj.scope)
    value = SimpleNamespace(object_name=key, last_modified=at)
    if bad == "key":
        value.object_name = "private-exports/v1/synthetic private name"
    elif bad == "scope":
        value.object_name = storage.object_key(uuid4(), target, scope=obj.scope)
    elif bad == "time":
        value.last_modified = at.replace(tzinfo=None)
    monkeypatch.setattr(
        client, "list_objects", lambda *args, **kwargs: iter([value]), raising=False
    )
    with pytest.raises(ArtifactError, match="LIST_FAILED") as exc:
        obj.page(generation=generation, after=key if bad == "order" else None)
    assert "synthetic private" not in str(exc.value)


@pytest.mark.parametrize("limit", [0, 101, True, 1.5])
def test_invalid_listing_limits_do_not_call_storage(adapter, limit):
    obj, client, _, _ = adapter
    with pytest.raises(ArtifactError, match="INVALID"):
        obj.page(limit=limit)
    assert not client.calls


def test_storage_namespace_separates_databases_schemas_and_keys_but_not_host_aliases(settings):
    from pydantic import SecretStr
    from sqlalchemy.engine import make_url

    url = make_url(settings.database_url.get_secret_value())

    def changed(**values):
        return settings.model_copy(update=values)

    native = storage.storage_scope(settings)
    assert native == storage.storage_scope(
        changed(
            database_url=SecretStr(
                url.set(host="postgres", port=55432).render_as_string(hide_password=False)
            )
        )
    )
    for variant in [
        changed(
            database_url=SecretStr(url.set(database="other").render_as_string(hide_password=False))
        ),
        changed(
            database_url=SecretStr(
                url.update_query_dict(
                    {"options": "-csearch_path=isolated,public"}
                ).render_as_string(hide_password=False)
            )
        ),
        changed(identity_lookup_key=SecretStr("different-synthetic-lookup-key-0123456789")),
    ]:
        assert storage.storage_scope(variant) != native
    assert "synthetic" not in native and len(native) == 64


def test_foreign_namespace_cursor_is_rejected_before_listing(adapter):
    obj, client, generation, target = adapter
    foreign = "1" * 64 if obj.scope != "1" * 64 else "2" * 64
    with pytest.raises(ArtifactError, match="INVALID"):
        obj.page(after=storage.object_key(generation, target, scope=foreign))
    assert not client.calls
