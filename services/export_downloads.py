"""ADR-048 owner-only streaming preparation and authorization."""

import hashlib
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import closing
from dataclasses import dataclass, field
from datetime import timedelta
from time import monotonic
from typing import Protocol
from uuid import UUID

import anyio
from sqlalchemy.orm import Session

from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_artifacts import Manifest, decode_chunk, parse_manifest, read_artifact
from services.export_processing import ExportStore
from services.identity import IdentityError, IdentityService


@dataclass(frozen=True)
class Download:
    size: int
    chunks: Generator[bytes, None, None] = field(repr=False)


def available(
    identity: IdentityService, db: Session, actor: UUID, target: UUID
) -> ExportGeneration:
    request = db.get(DataRequest, target)
    if request is None or request.user_id != actor:
        raise IdentityError("RESOURCE_NOT_FOUND", 404)
    if request.kind != "EXPORT":
        raise IdentityError("EXPORT_REQUIRED", 409)
    if request.completed_at and request.completed_at + timedelta(hours=24) <= identity.clock():
        raise IdentityError("EXPORT_EXPIRED", 410)
    job = db.get(ExportJob, target)
    generation = db.get(ExportGeneration, job.generation_id) if job and job.generation_id else None
    if (
        request.completed_at is None
        or job is None
        or job.status != "READY"
        or generation is None
        or generation.published_at != request.completed_at
        or generation.digest != request.export_digest
    ):
        raise IdentityError("EXPORT_NOT_READY", 409)
    if generation.expires_at is None or generation.expires_at <= identity.clock():
        raise IdentityError("EXPORT_EXPIRED", 410)
    return generation


def authorize(
    identity: IdentityService, token: str, target: UUID
) -> tuple[UUID, UUID, bytes, Manifest]:
    with identity.transaction() as db:
        actor = identity.authenticate(db, token, recent=True).user_id
        if not identity.rate(db, f"data-export:{actor}", 10, 60):
            raise IdentityError("RATE_LIMITED", 429)
        generation = available(identity, db, actor, target)
        try:
            if generation.encrypted_manifest is None:
                raise ValueError("Missing manifest")
            raw_manifest = identity.decrypt(generation.encrypted_manifest).encode()
            manifest = parse_manifest(raw_manifest, target, generation.id)
            if manifest.size != generation.size or manifest.digest != generation.digest:
                raise ValueError("Manifest metadata")
        except Exception:
            raise RuntimeError("Private export manifest unavailable") from None
        generation_id = generation.id
    return actor, generation_id, raw_manifest, manifest


def prepare(
    identity: IdentityService,
    storage: ExportStore,
    token: str,
    target: UUID,
    *,
    timer: Callable[[], float] = monotonic,
) -> Download:
    actor, generation_id, raw_manifest, manifest = authorize(identity, token, target)
    deadline = timer() + 300

    def fetch(object_id: UUID) -> bytes:
        if timer() >= deadline:
            raise RuntimeError("Export transfer deadline")
        return storage.get(generation_id, object_id)

    def stream() -> Generator[bytes, None, None]:
        try:
            with closing(
                read_artifact(
                    raw_manifest, identity, fetch, request_id=target, generation_id=generation_id
                )
            ) as source:
                for part in source:
                    if timer() >= deadline:
                        raise RuntimeError("Export transfer deadline")
                    with identity.transaction() as db:
                        current_actor = identity.authenticate(db, token, recent=True).user_id
                        current = available(identity, db, current_actor, target)
                        if current_actor != actor or current.id != generation_id:
                            raise RuntimeError("Export binding changed")
                    # Close the authority transaction before backpressure from a slow client.
                    yield part
        except Exception:
            raise RuntimeError("Private export transfer incomplete") from None

    return Download(manifest.size, stream())


class AsyncExportStore(Protocol):
    async def get(self, generation: UUID, object_id: UUID) -> bytes: ...

    async def aclose(self) -> None: ...


@dataclass(frozen=True)
class AsyncDownload:
    size: int
    chunks: AsyncGenerator[bytes, None] = field(repr=False)


async def prepare_async(
    identity: IdentityService,
    storage_factory: Callable[[], AsyncExportStore],
    token: str,
    target: UUID,
) -> AsyncDownload:
    actor, generation_id, _, manifest = await anyio.to_thread.run_sync(
        authorize, identity, token, target, abandon_on_cancel=True
    )

    def recheck() -> None:
        with identity.transaction() as db:
            current_actor = identity.authenticate(db, token, recent=True).user_id
            current = available(identity, db, current_actor, target)
            if current_actor != actor or current.id != generation_id:
                raise RuntimeError("Export binding changed")

    async def stream() -> AsyncGenerator[bytes, None]:
        storage = None
        try:
            storage = storage_factory()
            digest = hashlib.sha256()
            deadline = monotonic() + 300
            for chunk in manifest.chunks:
                with anyio.fail_after(max(0, deadline - monotonic())):
                    ciphertext = await storage.get(generation_id, chunk.object_id)
                    raw = decode_chunk(ciphertext, identity, chunk, target, generation_id)
                    digest.update(raw)
                    if (
                        chunk.ordinal == len(manifest.chunks) - 1
                        and digest.hexdigest() != manifest.digest
                    ):
                        raise RuntimeError("Export integrity mismatch")
                    await anyio.to_thread.run_sync(recheck, abandon_on_cancel=True)
                yield raw
        except Exception:
            raise RuntimeError("Private export transfer incomplete") from None
        finally:
            if storage is not None:
                try:
                    with anyio.fail_after(1, shield=True):
                        await storage.aclose()
                except Exception:
                    raise RuntimeError("Private export transfer incomplete") from None

    return AsyncDownload(manifest.size, stream())
