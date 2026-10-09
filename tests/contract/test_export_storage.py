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
def adapter(monkeypatch):
    client = Client()
    monkeypatch.setattr(
        storage,
        "MinioObjectStorage",
        lambda _: SimpleNamespace(client=client, container="synthetic"),
    )
    return storage.PrivateExportStorage(None), client, uuid4(), uuid4()


def test_private_keys_and_bounded_round_trip(adapter):
    obj, client, generation, target = adapter
    raw = b"x" * MAX_CIPHERTEXT_BYTES
    obj.put(generation, target, raw)
    assert client.stream.closed
    assert client.calls == [
        (
            "put",
            "synthetic",
            f"private-exports/v1/{generation}/{target}",
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
    assert client.calls[-1] == ("remove", "synthetic", f"private-exports/v1/{generation}/{target}")


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
