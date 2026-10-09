"""ADR-048 bounded synthetic/local export generation."""

import hmac
from collections.abc import Callable, Iterator
from time import monotonic
from typing import Protocol
from uuid import UUID

from services.data_export_projection import encoded_project
from services.export_artifacts import CHUNK_BYTES, MAX_BYTES, ArtifactError, write_artifact
from services.export_jobs import claim_next, fail_claim
from services.export_publication import ExportStopped, publish, snapshot
from services.identity import IdentityError, IdentityService
from services.observability import emit


class ExportStore(Protocol):
    def put(self, generation: UUID, object_id: UUID, ciphertext: bytes) -> None: ...

    def get(self, generation: UUID, object_id: UUID) -> bytes: ...


class GenerationLimit(RuntimeError):
    pass


def _process_one(
    identity: IdentityService, storage: ExportStore, *, timer: Callable[[], float] = monotonic
) -> bool:
    claim = claim_next(identity)
    if claim is None:
        return False
    emit("export.generation.started", str(claim.correlation_id), "WORKER", 202)
    deadline = timer() + 90
    limited = False

    def checkpoint() -> None:
        nonlocal limited
        if timer() >= deadline:
            limited = True
            raise GenerationLimit("EXPORT_LIMIT_REACHED")

    def put(object_id: UUID, raw: bytes) -> None:
        checkpoint()
        storage.put(claim.generation_id, object_id, raw)
        checkpoint()
        if not hmac.compare_digest(storage.get(claim.generation_id, object_id), raw):
            raise ArtifactError("EXPORT_OBJECT_VERIFICATION_FAILED")
        checkpoint()

    try:
        with snapshot(identity, claim) as reader:

            def source() -> Iterator[bytes]:
                nonlocal limited
                try:
                    yield from encoded_project(
                        identity,
                        reader,
                        claim.actor_id,
                        claim.request_id,
                        max_bytes=MAX_BYTES,
                        record_limit=100_000,
                        chunk_bytes=CHUNK_BYTES,
                        checkpoint=checkpoint,
                    )
                except IdentityError as error:
                    if error.code == "EXPORT_LIMIT_REACHED":
                        limited = True
                    raise

            raw_manifest = write_artifact(
                source(),
                identity,
                put,
                request_id=claim.request_id,
                generation_id=claim.generation_id,
            )
        checkpoint()
        publish(identity, claim, raw_manifest)
    except ExportStopped as error:
        fail_claim(identity, claim, error.reason)
        emit("export.generation.stopped", str(claim.correlation_id), "WORKER", 409)
        return False
    except Exception:
        fail_claim(identity, claim, "LIMIT_REACHED" if limited else "PROCESSING_FAILED")
        emit("export.generation.failed", str(claim.correlation_id), "WORKER", 503)
        return False
    emit("export.generation.ready", str(claim.correlation_id), "WORKER", 200)
    return True


def process_one(
    identity: IdentityService, storage: ExportStore, *, timer: Callable[[], float] = monotonic
) -> bool:
    try:
        return _process_one(identity, storage, timer=timer)
    except Exception:
        # A database outage during claiming/failure recording must not leak provider diagnostics.
        # An unacknowledged claim remains recoverable through its finite lease.
        raise RuntimeError("Personal export processing failed; diagnostics withheld") from None
