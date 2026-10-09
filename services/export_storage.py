"""Private local object adapter for ADR-047; lifecycle policy remains with its caller."""

import hashlib
import hmac
import json
import re
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from itertools import islice
from uuid import UUID

from sqlalchemy.engine import make_url

from services.config import Settings
from services.export_artifacts import MAX_CIPHERTEXT_BYTES, ArtifactError
from services.providers import MinioObjectStorage

PREFIX = "private-exports/v1"


def storage_scope(settings: Settings) -> str:
    url = make_url(settings.database_url.get_secret_value())
    value = json.dumps(
        {"database": url.database, "options": url.query.get("options", "")}, sort_keys=True
    )
    return hmac.new(
        settings.identity_lookup_key.get_secret_value().encode(),
        ("export-object-scope:" + value).encode(),
        hashlib.sha256,
    ).hexdigest()


def object_key(generation: UUID, object_id: UUID, *, scope: str) -> str:
    if (
        type(generation) is not UUID
        or type(object_id) is not UUID
        or not isinstance(scope, str)
        or re.fullmatch(r"[a-f0-9]{64}", scope) is None
    ):
        raise ArtifactError("EXPORT_OBJECT_INVALID")
    return f"{PREFIX}/{scope}/{generation}/{object_id}"


@dataclass(frozen=True)
class StoredExportObject:
    generation: UUID
    object_id: UUID
    modified_at: datetime
    scope: str

    @property
    def key(self) -> str:
        return object_key(self.generation, self.object_id, scope=self.scope)


def parse_key(key: str, *, scope: str | None = None) -> tuple[UUID, UUID]:
    try:
        prefix, found_scope, generation, target = key.rsplit("/", 3)
        ids = UUID(generation), UUID(target)
        if (
            prefix != PREFIX
            or object_key(*ids, scope=found_scope) != key
            or scope is not None
            and found_scope != scope
        ):
            raise ValueError("Object prefix")
        return ids
    except Exception:
        raise ArtifactError("EXPORT_OBJECT_INVALID") from None


class PrivateExportStorage:
    """Bounded private-prefix access; no public URLs or independent retention decisions."""

    def __init__(self, settings: Settings) -> None:
        storage = MinioObjectStorage(settings)
        self.client, self.container = storage.client, storage.container
        self.scope = storage_scope(settings)

    def put(self, generation: UUID, object_id: UUID, ciphertext: bytes) -> None:
        key = object_key(generation, object_id, scope=self.scope)
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
        key = object_key(generation, object_id, scope=self.scope)
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
        key = object_key(generation, object_id, scope=self.scope)
        try:
            self.client.remove_object(self.container, key)
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_DELETE_FAILED") from None

    def page(
        self, *, generation: UUID | None = None, after: str | None = None, limit: int = 100
    ) -> list[StoredExportObject]:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ArtifactError("EXPORT_OBJECT_INVALID")
        if after is not None:
            ids = parse_key(after, scope=self.scope)
            if generation is not None and ids[0] != generation:
                raise ArtifactError("EXPORT_OBJECT_INVALID")
        prefix = PREFIX + "/" + self.scope + "/"
        if generation is not None:
            if type(generation) is not UUID:
                raise ArtifactError("EXPORT_OBJECT_INVALID")
            prefix += str(generation) + "/"
        source = None
        try:
            source = self.client.list_objects(
                self.container, prefix=prefix, recursive=True, start_after=after
            )
            result = []
            previous = after
            for value in islice(source, limit):
                owner, target = parse_key(value.object_name or "", scope=self.scope)
                key = object_key(owner, target, scope=self.scope)
                if previous is not None and key <= previous:
                    raise ValueError("Object ordering")
                previous = key
                if generation is not None and owner != generation:
                    raise ValueError("Object scope")
                at = value.last_modified
                if not isinstance(at, datetime) or at.utcoffset() is None:
                    raise ValueError("Object time")
                result.append(StoredExportObject(owner, target, at, self.scope))
            return result
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_LIST_FAILED") from None
        finally:
            if isinstance(source, Generator):
                try:
                    source.close()
                except Exception:
                    raise ArtifactError("EXPORT_OBJECT_LIST_FAILED") from None
