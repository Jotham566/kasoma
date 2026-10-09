"""Private artifact boundary with synthetic bytes, real local crypto and fake object storage."""

import base64
import json
from contextlib import closing
from uuid import UUID, uuid4

import pytest
from cryptography.fernet import Fernet

from services import export_artifacts as artifacts
from services.export_artifacts import ArtifactError, parse_manifest, read_artifact, write_artifact


class TestCipher:
    __test__ = False

    def __init__(self, key=b"S" * 32):
        self.cipher = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, value):
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, value):
        return self.cipher.decrypt(value.encode()).decode()


@pytest.fixture
def store():
    cipher, objects = TestCipher(), {}
    binding = {"request_id": uuid4(), "generation_id": uuid4()}
    return cipher, objects, binding


def save(store, parts):
    cipher, objects, binding = store
    return write_artifact(iter(parts), cipher, objects.__setitem__, **binding)


def read(store, manifest):
    cipher, objects, binding = store
    return read_artifact(manifest, cipher, objects.__getitem__, **binding)


def test_round_trip_private_bound_chunks_and_manifest(store):
    parts = [b'{"synthetic":', '"π"}'.encode()]
    manifest = save(store, parts)
    cipher, objects, binding = store
    result = parse_manifest(manifest, **binding)
    assert result.size == sum(map(len, parts))
    assert list(read(store, manifest)) == parts
    assert all(isinstance(key, UUID) for key in objects)
    for chunk in result.chunks:
        encrypted = objects[chunk.object_id]
        assert b"synthetic" not in encrypted
        assert str(binding["request_id"]).encode() not in encrypted
        envelope = json.loads(cipher.decrypt(encrypted.decode()))
        assert envelope["request_id"] == str(binding["request_id"])
        assert envelope["generation_id"] == str(binding["generation_id"])
        assert envelope["ordinal"] == chunk.ordinal
        assert base64.b64decode(envelope["payload"]) == parts[chunk.ordinal]
    assert len(manifest) < artifacts.MAX_MANIFEST_BYTES
    assert "payload" not in repr(
        artifacts.Envelope.model_validate_json(cipher.decrypt(encrypted.decode()))
    )


def test_exact_size_and_chunk_count_boundaries(store):
    # 16 MiB is the private format ceiling, not an increase to the synchronous route cap.
    part = b"x" * artifacts.CHUNK_BYTES
    manifest = save(store, (part for _ in range(artifacts.MAX_CHUNKS)))
    result = parse_manifest(manifest, **store[2])
    assert result.size == artifacts.MAX_BYTES
    assert sum(map(len, read(store, manifest))) == artifacts.MAX_BYTES
    assert all(len(raw) <= artifacts.MAX_CIPHERTEXT_BYTES for raw in store[1].values())
    with pytest.raises(ArtifactError, match="WRITE_FAILED"):
        save(store, [b"x"] * (artifacts.MAX_CHUNKS + 1))


@pytest.mark.parametrize("parts", [[], [b""], [b"x" * (artifacts.CHUNK_BYTES + 1)], ["text"]])
def test_empty_or_oversized_source_is_not_published(store, parts):
    with pytest.raises(ArtifactError, match="WRITE_FAILED"):
        save(store, parts)
    assert not store[1]


@pytest.mark.parametrize("field", ["request_id", "generation_id"])
def test_wrong_manifest_binding_reads_no_objects(store, field):
    manifest = save(store, [b"synthetic"])
    binding = store[2] | {field: uuid4()}
    with pytest.raises(ArtifactError, match="INVALID"):
        list(read_artifact(manifest, store[0], lambda _: pytest.fail("No read"), **binding))


@pytest.mark.parametrize(
    "change", ["extra", "gap", "duplicate", "size", "format", "empty", "float", "missing_format"]
)
def test_manifest_corruption_reads_no_objects(store, change):
    data = json.loads(save(store, [b"first", b"second"]))
    if change == "extra":
        data["sensitive"] = "synthetic secret"
    elif change == "gap":
        data["chunks"][1]["ordinal"] = 2
    elif change == "duplicate":
        data["chunks"][1]["object_id"] = data["chunks"][0]["object_id"]
    elif change == "size":
        data["size"] += 1
    elif change == "format":
        data["format"] = "unknown"
    elif change == "missing_format":
        del data["format"]
    elif change == "empty":
        data["chunks"] = []
    elif change == "float":
        data["chunks"][0]["size"] = 5.0
    with pytest.raises(ArtifactError, match="INVALID") as exc:
        list(
            read_artifact(
                json.dumps(data).encode(), store[0], lambda _: pytest.fail("No read"), **store[2]
            )
        )
    assert "synthetic secret" not in str(exc.value)
    assert exc.value.__suppress_context__


def test_oversized_or_invalid_manifest_fails_before_storage(store):
    for raw in [b"", b"broken", b"x" * (artifacts.MAX_MANIFEST_BYTES + 1), "text"]:
        with pytest.raises(ArtifactError, match="INVALID"):
            list(read_artifact(raw, store[0], lambda _: pytest.fail("No read"), **store[2]))


@pytest.mark.parametrize(
    "change",
    ["request_id", "generation_id", "ordinal", "payload", "extra", "base64", "missing_format"],
)
def test_authenticated_but_wrong_envelope_is_rejected(store, change):
    manifest = save(store, [b"first", b"second"])
    cipher, objects, _ = store
    key = next(iter(objects))
    data = json.loads(cipher.decrypt(objects[key].decode()))
    if change in {"request_id", "generation_id"}:
        data[change] = str(uuid4())
    elif change == "ordinal":
        data[change] = 1
    elif change == "payload":
        data[change] = base64.b64encode(b"WRONG").decode()
    elif change == "missing_format":
        del data["format"]
    elif change == "extra":
        data[change] = "synthetic private"
    else:
        data["payload"] = "!!!!"
    objects[key] = cipher.encrypt(json.dumps(data)).encode()
    with pytest.raises(ArtifactError, match="READ_FAILED"):
        next(read(store, manifest))


@pytest.mark.parametrize(
    "change", ["swap", "missing", "truncate", "corrupt", "oversize", "wrong_key"]
)
def test_storage_and_cipher_failures_are_closed_before_yield(store, change):
    manifest = save(store, [b"first", b"second"])
    cipher, objects, binding = store
    keys = list(objects)
    if change == "swap":
        objects[keys[0]] = objects[keys[1]]
    elif change == "missing":
        del objects[keys[0]]
    elif change == "truncate":
        objects[keys[0]] = objects[keys[0]][:-10]
    elif change == "corrupt":
        objects[keys[0]] = b"synthetic secret diagnostics"
    elif change == "oversize":
        objects[keys[0]] = b"x" * (artifacts.MAX_CIPHERTEXT_BYTES + 1)
    else:
        cipher = TestCipher(b"T" * 32)
    with pytest.raises(ArtifactError, match="READ_FAILED") as exc:
        next(read_artifact(manifest, cipher, objects.__getitem__, **binding))
    assert str(exc.value) == "EXPORT_ARTIFACT_READ_FAILED"
    assert exc.value.__suppress_context__


def test_whole_file_integrity_is_checked_before_last_chunk(store):
    data = json.loads(save(store, [b"first", b"last"]))
    data["digest"] = "0" * 64
    with closing(read(store, json.dumps(data).encode())) as source:
        assert next(source) == b"first"
        with pytest.raises(ArtifactError, match="READ_FAILED"):
            next(source)


def test_cancellation_does_not_fetch_remaining_objects(store):
    manifest = save(store, [b"first", b"last"])
    calls = []

    def fetch(key):
        calls.append(key)
        return store[1][key]

    with closing(read_artifact(manifest, store[0], fetch, **store[2])) as source:
        assert next(source) == b"first"
    assert len(calls) == 1


def test_failed_upload_closes_source_and_returns_no_manifest(store):
    consumed, closed = [], []

    def source():
        try:
            for i in range(4):
                consumed.append(i)
                yield b"synthetic"
        finally:
            closed.append(True)

    def upload(key, value):
        if store[1]:
            raise RuntimeError("synthetic secret storage URL")
        store[1][key] = value

    with pytest.raises(ArtifactError, match="WRITE_FAILED") as exc:
        write_artifact(source(), store[0], upload, **store[2])
    assert consumed == [0, 1] and closed == [True]
    assert len(store[1]) == 1  # Caller must clean unpublished objects; never a completion manifest.
    assert str(exc.value) == "EXPORT_ARTIFACT_WRITE_FAILED"
    assert exc.value.__suppress_context__


def test_source_cleanup_errors_are_minimized(store):
    def source():
        try:
            yield b"x" * (artifacts.CHUNK_BYTES + 1)
        finally:
            raise RuntimeError("synthetic secret cleanup error")

    with pytest.raises(ArtifactError) as exc:
        write_artifact(source(), store[0], store[1].__setitem__, **store[2])
    assert str(exc.value) == "EXPORT_ARTIFACT_WRITE_FAILED"


@pytest.mark.parametrize("result", ["", "x" * (artifacts.MAX_CIPHERTEXT_BYTES + 1), "π"])
def test_invalid_encrypted_output_is_never_uploaded(store, result):
    class BrokenCipher(TestCipher):
        def encrypt(self, value):
            return result

    with pytest.raises(ArtifactError, match="WRITE_FAILED"):
        write_artifact(iter([b"synthetic"]), BrokenCipher(), store[1].__setitem__, **store[2])
    assert not store[1]


def test_bad_decryption_implementation_cannot_return_unbounded_envelope(store):
    manifest = save(store, [b"synthetic"])

    class BrokenCipher(TestCipher):
        def decrypt(self, value):
            return "x" * (artifacts.MAX_CIPHERTEXT_BYTES + 1)

    with pytest.raises(ArtifactError, match="READ_FAILED"):
        next(read_artifact(manifest, BrokenCipher(), store[1].__getitem__, **store[2]))
