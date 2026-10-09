"""ADR-047 local MinIO verification; create and remove only this test's random objects."""

from uuid import uuid4

import anyio
import httpx
import pytest
from cryptography.fernet import Fernet

from services.config import Settings
from services.export_artifacts import ArtifactError, parse_manifest, read_artifact, write_artifact
from services.export_reader import PrivateExportReader
from services.export_storage import PrivateExportStorage, object_key

pytestmark = pytest.mark.integration


class LocalCipher:
    def __init__(self, settings):
        self.cipher = Fernet(settings.identity_encryption_key.get_secret_value().encode())

    def encrypt(self, value):
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, value):
        return self.cipher.decrypt(value.encode()).decode()


def test_private_minio_artifact_round_trip_and_owned_cleanup():
    settings = Settings()
    adapter, cipher = PrivateExportStorage(settings), LocalCipher(settings)
    request, generation = uuid4(), uuid4()
    owned = []
    parts = [b"synthetic private test bytes " * 2000, b"final synthetic bytes"]

    def put(object_id, value):
        owned.append(object_id)  # A failed acknowledgement can still leave an object.
        adapter.put(generation, object_id, value)

    try:
        manifest = write_artifact(
            iter(parts), cipher, put, request_id=request, generation_id=generation
        )
        entries = adapter.page(generation=generation)
        assert {entry.object_id for entry in entries} == set(owned)
        assert all(entry.scope == adapter.scope for entry in entries)
        parsed = parse_manifest(manifest, request, generation)
        assert parsed.size == sum(map(len, parts))
        expected_ciphertext = [adapter.get(generation, target) for target in owned]

        async def private_reads():
            reader = PrivateExportReader(settings)
            try:
                for target, expected in zip(owned, expected_ciphertext, strict=True):
                    assert await reader.get(generation, target) == expected
            finally:
                await reader.aclose()

        anyio.run(private_reads)
        assert (
            list(
                read_artifact(
                    manifest,
                    cipher,
                    lambda target: adapter.get(generation, target),
                    request_id=request,
                    generation_id=generation,
                )
            )
            == parts
        )
        with httpx.Client(trust_env=False, timeout=5) as client:
            key = object_key(generation, owned[0], scope=adapter.scope)
            endpoint = settings.object_storage_endpoint.rstrip("/")
            result = client.get(f"{endpoint}/{settings.object_storage_container}/{key}")
            assert result.status_code == 403
        with pytest.raises(ArtifactError, match="READ_FAILED"):
            adapter.get(uuid4(), owned[0])
    finally:
        # Never list, clear a bucket or remove any object not created by this invocation.
        cleanup_failed = False
        for target in owned:
            try:
                adapter.remove(generation, target)
            except ArtifactError:
                cleanup_failed = True
        assert not cleanup_failed, "Owned synthetic object cleanup failed"
    for target in owned:
        with pytest.raises(ArtifactError, match="READ_FAILED"):
            adapter.get(generation, target)
