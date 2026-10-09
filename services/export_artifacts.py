"""ADR-047 authenticated bounded artifact format; no publication or learner delivery."""

import base64
import hashlib
from collections.abc import Callable, Generator, Iterator
from typing import Final, Literal, Protocol, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

CHUNK_BYTES = 64 * 1024
MAX_CHUNKS = 256
MAX_BYTES = CHUNK_BYTES * MAX_CHUNKS
MAX_CIPHERTEXT_BYTES = 128 * 1024
MAX_MANIFEST_BYTES = 64 * 1024
FORMAT: Final = "kasoma-private-export-chunks-v1"


class ArtifactError(RuntimeError):
    """Closed operational error; never includes storage or plaintext diagnostics."""


class Cipher(Protocol):
    def encrypt(self, value: str) -> str: ...

    def decrypt(self, value: str) -> str: ...


class PrivateContract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, hide_input_in_errors=True)


class Chunk(PrivateContract):
    ordinal: int = Field(ge=0, lt=MAX_CHUNKS)
    object_id: UUID
    size: int = Field(ge=1, le=CHUNK_BYTES)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class Manifest(PrivateContract):
    format: Literal["kasoma-private-export-chunks-v1"]
    request_id: UUID
    generation_id: UUID
    size: int = Field(ge=1, le=MAX_BYTES)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    chunks: tuple[Chunk, ...] = Field(min_length=1, max_length=MAX_CHUNKS)

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if (
            sum(chunk.size for chunk in self.chunks) != self.size
            or len({chunk.object_id for chunk in self.chunks}) != len(self.chunks)
            or any(chunk.ordinal != index for index, chunk in enumerate(self.chunks))
        ):
            raise ValueError("Invalid artifact manifest")
        return self


class Envelope(PrivateContract):
    format: Literal["kasoma-private-export-chunks-v1"]
    request_id: UUID
    generation_id: UUID
    ordinal: int = Field(ge=0, lt=MAX_CHUNKS)
    payload: str = Field(min_length=4, max_length=4 * ((CHUNK_BYTES + 2) // 3), repr=False)


def parse_manifest(raw: bytes, request_id: UUID, generation_id: UUID) -> Manifest:
    try:
        if type(raw) is not bytes or not 0 < len(raw) <= MAX_MANIFEST_BYTES:
            raise ValueError("Manifest size")
        result = Manifest.model_validate_json(raw)
        if (result.request_id, result.generation_id) != (request_id, generation_id):
            raise ValueError("Manifest binding")
        return result
    except Exception:
        raise ArtifactError("EXPORT_ARTIFACT_INVALID") from None


def write_artifact(
    source: Iterator[bytes],
    cipher: Cipher,
    write: Callable[[UUID, bytes], None],
    *,
    request_id: UUID,
    generation_id: UUID,
) -> bytes:
    """Return a bounded manifest only after uploads; caller owns orphan cleanup/publication."""
    try:
        chunks: list[Chunk] = []
        digest = hashlib.sha256()
        total = 0
        for raw in source:
            if type(raw) is not bytes or not 0 < len(raw) <= CHUNK_BYTES:
                raise ValueError("Chunk size")
            if len(chunks) >= MAX_CHUNKS:
                raise ValueError("Artifact size")
            chunk = Chunk(
                ordinal=len(chunks),
                object_id=uuid4(),
                size=len(raw),
                digest=hashlib.sha256(raw).hexdigest(),
            )
            envelope = Envelope(
                format=FORMAT,
                request_id=request_id,
                generation_id=generation_id,
                ordinal=chunk.ordinal,
                payload=base64.b64encode(raw).decode("ascii"),
            )
            ciphertext = cipher.encrypt(envelope.model_dump_json()).encode("ascii")
            if not 0 < len(ciphertext) <= MAX_CIPHERTEXT_BYTES:
                raise ValueError("Ciphertext size")
            write(chunk.object_id, ciphertext)
            chunks.append(chunk)
            digest.update(raw)
            total += len(raw)
        manifest = (
            Manifest(
                format=FORMAT,
                request_id=request_id,
                generation_id=generation_id,
                size=total,
                digest=digest.hexdigest(),
                chunks=tuple(chunks),
            )
            .model_dump_json()
            .encode()
        )
        if len(manifest) > MAX_MANIFEST_BYTES:
            raise ValueError("Manifest size")
        return manifest
    except Exception:
        raise ArtifactError("EXPORT_ARTIFACT_WRITE_FAILED") from None
    finally:
        if isinstance(source, Generator):
            try:
                source.close()
            except Exception:
                raise ArtifactError("EXPORT_ARTIFACT_WRITE_FAILED") from None


def read_artifact(
    raw_manifest: bytes,
    cipher: Cipher,
    read: Callable[[UUID], bytes],
    *,
    request_id: UUID,
    generation_id: UUID,
) -> Generator[bytes, None, None]:
    """Verify each chunk before yielding; verify the whole file before its final chunk."""
    manifest = parse_manifest(raw_manifest, request_id, generation_id)
    digest = hashlib.sha256()
    for chunk in manifest.chunks:
        try:
            ciphertext = read(chunk.object_id)
            if type(ciphertext) is not bytes or not 0 < len(ciphertext) <= MAX_CIPHERTEXT_BYTES:
                raise ValueError("Ciphertext size")
            plaintext = cipher.decrypt(ciphertext.decode("ascii"))
            # Bound malicious/misconfigured cipher implementations as well as storage input.
            if len(plaintext) > MAX_CIPHERTEXT_BYTES:
                raise ValueError("Envelope size")
            envelope = Envelope.model_validate_json(plaintext)
            if (envelope.request_id, envelope.generation_id, envelope.ordinal) != (
                request_id,
                generation_id,
                chunk.ordinal,
            ):
                raise ValueError("Chunk binding")
            raw = base64.b64decode(envelope.payload, validate=True)
            if len(raw) != chunk.size or hashlib.sha256(raw).hexdigest() != chunk.digest:
                raise ValueError("Chunk integrity")
            digest.update(raw)
            if chunk.ordinal == len(manifest.chunks) - 1 and digest.hexdigest() != manifest.digest:
                raise ValueError("Artifact integrity")
        except Exception:
            raise ArtifactError("EXPORT_ARTIFACT_READ_FAILED") from None
        yield raw
