"""Private local object adapter for ADR-047; lifecycle policy remains with its caller."""

from io import BytesIO
from uuid import UUID

from services.config import Settings
from services.export_artifacts import MAX_CIPHERTEXT_BYTES, ArtifactError
from services.providers import MinioObjectStorage

PREFIX = "private-exports/v1"


def object_key(generation: UUID, object_id: UUID) -> str:
    if type(generation) is not UUID or type(object_id) is not UUID:
        raise ArtifactError("EXPORT_OBJECT_INVALID")
    return f"{PREFIX}/{generation}/{object_id}"


class PrivateExportStorage:
    """No bucket creation, listing, public URLs, automatic retries or retention decisions."""

    def __init__(self, settings: Settings) -> None:
        storage = MinioObjectStorage(settings)
        self.client, self.container = storage.client, storage.container

    def put(self, generation: UUID, object_id: UUID, ciphertext: bytes) -> None:
        key = object_key(generation, object_id)
        try:
            if type(ciphertext) is not bytes or not 0 < len(ciphertext) <= MAX_CIPHERTEXT_BYTES:
                raise ValueError("Object size")
            with BytesIO(ciphertext) as stream:
                self.client.put_object(
                    self.container,
                    key,
                    stream,
                    len(ciphertext),
                    content_type="application/octet-stream",
                )
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_WRITE_FAILED") from None

    def get(self, generation: UUID, object_id: UUID) -> bytes:
        key = object_key(generation, object_id)
        response = None
        try:
            response = self.client.get_object(self.container, key)
            header = response.headers.get("Content-Length", "")
            if not header.isascii() or not header.isdecimal() or len(header) > 6:
                raise ValueError("Object length")
            size = int(header)
            if not 0 < size <= MAX_CIPHERTEXT_BYTES:
                raise ValueError("Object size")
            # One extra byte detects an inconsistent provider without an unbounded read.
            raw = response.read(size + 1)
            if type(raw) is not bytes or len(raw) != size:
                raise ValueError("Incomplete or oversized object")
            return raw
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_READ_FAILED") from None
        finally:
            if response is not None:
                try:
                    try:
                        response.close()
                    finally:
                        response.release_conn()
                except Exception:
                    raise ArtifactError("EXPORT_OBJECT_READ_FAILED") from None

    def remove(self, generation: UUID, object_id: UUID) -> None:
        # The caller must authorize expiry/orphan cleanup; this is not a policy bypass route.
        key = object_key(generation, object_id)
        try:
            self.client.remove_object(self.container, key)
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_DELETE_FAILED") from None
