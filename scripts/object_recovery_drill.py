"""NFR-REL-002: restore synthetic PostgreSQL and actual private MinIO objects."""

import json
import os
import secrets
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from time import monotonic, sleep
from uuid import UUID, uuid4

import httpx
from cryptography.fernet import Fernet
from pydantic import SecretStr
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from scripts.disposable_owner import create_owner
from scripts.recovery_channel_preservation import verify_preservation
from scripts.recovery_containers import OwnedServices, RecoveryCommandError, command, compose_image
from scripts.recovery_drill import (
    check_guards,
    inventory,
    local_database_url,
    verify_retirement_disabled,
)
from scripts.recovery_exports import RecoveryExport
from scripts.recovery_fixture import populate
from scripts.recovery_short_text import verify_short_text
from services.config import Settings
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_artifacts import (
    MAX_CHUNKS,
    MAX_CIPHERTEXT_BYTES,
    ArtifactError,
    parse_manifest,
)
from services.export_storage import PrivateExportStorage
from services.identity import IdentityService
from services.observability import logger
from services.providers import FakeMessagingProvider, MinioObjectStorage


@contextmanager
def quiet_fixture_events() -> Iterator[None]:
    """Minimized aggregate reports in this standalone synthetic process only."""
    original = logger.disabled
    logger.disabled = True
    try:
        yield
    finally:
        logger.disabled = original


@dataclass(repr=False)
class StoredExport(RecoveryExport):
    storage: PrivateExportStorage | None = None

    def get(self, generation: UUID, object_id: UUID) -> bytes:
        if self.storage is None:
            raise ValueError("RECOVERY_OBJECT_STORAGE_REQUIRED")
        return self.storage.get(generation, object_id)


def references(identity: IdentityService, target: UUID | None) -> tuple[UUID, tuple[UUID, ...]]:
    if target is None:
        raise ValueError("RECOVERY_EXPORT_REQUIRED")
    with Session(identity.engine) as db:
        job = db.get(ExportJob, target)
        generation = db.get(ExportGeneration, job.generation_id) if job else None
        if generation is None or generation.encrypted_manifest is None:
            raise ValueError("RECOVERY_MANIFEST_REQUIRED")
        manifest = parse_manifest(
            identity.decrypt(generation.encrypted_manifest).encode(), target, generation.id
        )
        return generation.id, tuple(chunk.object_id for chunk in manifest.chunks)


def backup_objects(
    source: PrivateExportStorage,
    generation: UUID,
    objects: tuple[UUID, ...],
    directory: Path,
) -> tuple[tuple[UUID, int], ...]:
    if not 1 <= len(objects) <= MAX_CHUNKS or len(set(objects)) != len(objects):
        raise ValueError("RECOVERY_OBJECT_INVENTORY_INVALID")
    result = []
    for object_id in objects:
        if type(object_id) is not UUID:
            raise ValueError("RECOVERY_OBJECT_ID_INVALID")
        raw = source.get(generation, object_id)
        if type(raw) is not bytes or not 0 < len(raw) <= MAX_CIPHERTEXT_BYTES:
            raise ValueError("RECOVERY_OBJECT_SIZE_INVALID")
        with (directory / str(object_id)).open("xb") as output:
            os.fchmod(output.fileno(), 0o600)
            output.write(raw)
        result.append((object_id, len(raw)))
    return tuple(result)


def restore_objects(
    destination: PrivateExportStorage,
    generation: UUID,
    objects: tuple[tuple[UUID, int], ...],
    directory: Path,
) -> int:
    if not 1 <= len(objects) <= MAX_CHUNKS or len({value[0] for value in objects}) != len(objects):
        raise ValueError("RECOVERY_OBJECT_INVENTORY_INVALID")
    total = 0
    for object_id, size in objects:
        if (
            type(object_id) is not UUID
            or type(size) is not int
            or not 0 < size <= MAX_CIPHERTEXT_BYTES
        ):
            raise ValueError("RECOVERY_OBJECT_INVENTORY_INVALID")
        with (directory / str(object_id)).open("rb") as data:
            raw = data.read(MAX_CIPHERTEXT_BYTES + 1)
        if len(raw) != size:
            raise ValueError("RECOVERY_OBJECT_SIZE_INVALID")
        destination.put(generation, object_id, raw)
        if destination.get(generation, object_id) != raw:
            raise ValueError("RECOVERY_OBJECT_COPY_MISMATCH")
        total += len(raw)
    return total


def verify_faults(
    identity: IdentityService, state: StoredExport, generation: UUID, target: UUID
) -> None:
    storage = state.storage
    if storage is None:
        raise ValueError("RECOVERY_OBJECT_STORAGE_REQUIRED")
    raw = storage.get(generation, target)
    for fault in ("MISSING", "CORRUPT"):
        try:
            if fault == "MISSING":
                storage.remove(generation, target)
            else:
                storage.put(generation, target, bytes([raw[0] ^ 1]) + raw[1:])
            try:
                state.verify(identity)
            except ArtifactError as error:
                if str(error) != "EXPORT_ARTIFACT_READ_FAILED":
                    raise ValueError("RECOVERY_UNEXPECTED_REJECTION") from None
            else:
                raise ValueError("RECOVERY_CORRUPT_OBJECT_ACCEPTED")
        finally:
            storage.put(generation, target, raw)
        state.verify(identity)


def wait_database(cid: str) -> None:
    deadline = monotonic() + 45
    while monotonic() < deadline:
        try:
            command(["docker", "exec", cid, "pg_isready", "-U", "kasoma"])
            return
        except RecoveryCommandError:
            sleep(0.2)
    raise ValueError("RECOVERY_DATABASE_START_TIMEOUT")


def wait_objects(port: int) -> None:
    deadline = monotonic() + 45
    with httpx.Client(timeout=1, trust_env=False) as client:
        while monotonic() < deadline:
            try:
                ready = client.get(f"http://127.0.0.1:{port}/minio/health/live").status_code == 200
            except httpx.HTTPError:
                ready = False
            if ready:
                return
            sleep(0.2)
    raise ValueError("RECOVERY_OBJECT_START_TIMEOUT")


def fresh_settings(
    base: Settings, database: str, password: str, access: str, secret: str
) -> Settings:
    return base.model_copy(
        update={
            "app_env": "development",
            "database_url": SecretStr(
                URL.create(
                    "postgresql+psycopg",
                    username="kasoma",
                    password=password,
                    host="127.0.0.1",
                    database=database,
                ).render_as_string(hide_password=False)
            ),
            "object_storage_container": "synthetic-recovery",
            "object_storage_access_key": SecretStr(access),
            "object_storage_secret_key": SecretStr(secret),
            "identity_encryption_key": SecretStr(Fernet.generate_key().decode()),
            "identity_lookup_key": SecretStr(secrets.token_urlsafe(48)),
            "jwt_signing_key": SecretStr(secrets.token_urlsafe(48)),
            "model_provider": "fake",
            "email_provider": "fake",
            "sms_provider": "fake",
            "whatsapp_provider": "fake",
            "allow_external_api_calls": False,
            "allow_google_free_tier_eval": False,
            "whatsapp_outbound_enabled": False,
            "otp_observation_enabled": False,
            "model_observation_enabled": False,
            "export_retirement_enabled": False,
            "short_text_enabled": False,
            "channel_preservation_enabled": False,
            "channel_receipt_holds_enabled": False,
            "export_evidence_holds_enabled": False,
            "whatsapp_app_secret": SecretStr(secrets.token_urlsafe(32)),
            "whatsapp_verify_token": SecretStr(secrets.token_urlsafe(32)),
            "token_issuer": "kasoma-synthetic-recovery",
        }
    )


def at_services(settings: Settings, services: OwnedServices, side: str) -> Settings:
    from sqlalchemy.engine import make_url

    url = make_url(settings.database_url.get_secret_value()).set(port=services.port(side + "-db"))
    return settings.model_copy(
        update={
            "database_url": SecretStr(url.render_as_string(hide_password=False)),
            "object_storage_endpoint": f"http://127.0.0.1:{services.port(side + '-objects')}",
        }
    )


def drill(settings: Settings) -> dict[str, object]:
    local_database_url(settings)  # Reject unsafe profiles before any Docker/resource operation.
    services = OwnedServices(uuid4().hex)
    result: dict[str, object] = {"status": "FAILED", "profile": "isolated-synthetic-db-objects-v1"}
    engines: list[Engine] = []
    stage = "RESOLVE_APPROVED_LOCAL_IMAGES"
    try:
        postgres, minio = compose_image("postgres"), compose_image("minio")
        database = "kasoma_drill_src_" + services.invocation
        password, access, secret = (
            secrets.token_urlsafe(32),
            secrets.token_hex(10),
            secrets.token_urlsafe(32),
        )
        synthetic = fresh_settings(settings, database, password, access, secret)
        stage = "CREATE_OWNED_SERVICES"
        for side in ("source", "destination"):
            cid = services.create(
                side + "-db",
                postgres,
                {
                    "POSTGRES_USER": "kasoma",
                    "POSTGRES_PASSWORD": password,
                    "POSTGRES_DB": database,
                },
            )
            services.create(
                side + "-objects", minio, {"MINIO_ROOT_USER": access, "MINIO_ROOT_PASSWORD": secret}
            )
            wait_database(cid)
            wait_objects(services.port(side + "-objects"))
        source, destination = (
            at_services(synthetic, services, side) for side in ("source", "destination")
        )
        source_engine, restored_engine = (
            create_engine(value.database_url.get_secret_value(), hide_parameters=True)
            for value in (source, destination)
        )
        engines.extend([source_engine, restored_engine])
        stage = "MIGRATE_SYNTHETIC_SOURCE"
        create_owner(source_engine, database)
        subprocess.run(
            ["make", "migrate"],
            env=dict(os.environ, DATABASE_URL=source.database_url.get_secret_value()),
            capture_output=True,
            check=True,
            timeout=120,
        )
        stage = "POPULATE_SYNTHETIC_SOURCE"
        with quiet_fixture_events():
            fixture = populate(source)
        fake = FakeMessagingProvider()
        original = IdentityService(source_engine, source, fake, fake)
        restored = IdentityService(restored_engine, destination, fake, fake)
        source_storage, destination_storage = (
            PrivateExportStorage(source),
            PrivateExportStorage(destination),
        )
        if source_storage.scope != destination_storage.scope:
            raise ValueError("RECOVERY_STORAGE_SCOPE_MISMATCH")
        for configuration in (source, destination):
            MinioObjectStorage(configuration).ensure_container()
        # Original fixture publication is quiescent and synthetic. Replace its
        # in-memory transport with real source MinIO before taking recovery evidence.
        for (generation, object_id), raw in fixture.objects.items():
            source_storage.put(generation, object_id, raw)
        fixture.objects.clear()
        source_export = StoredExport(
            target=fixture.target, frozen=fixture.frozen, storage=source_storage
        )
        source_export.verify(original)
        generation, objects = references(original, fixture.target)
        before = inventory(source_engine)
        vector_query = text("SELECT extversion FROM pg_extension WHERE extname='vector'")
        with source_engine.connect() as left:
            source_vector = left.scalar(vector_query)
        if not source_vector:
            raise ValueError("RECOVERY_SOURCE_VECTOR_MISSING")
        if len(before) == 0 or not objects:
            raise ValueError("RECOVERY_FIXTURE_EMPTY")
        Path(".local").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="object-recovery-", dir=".local") as directory:
            dump = Path(directory) / "synthetic.dump"
            stage = "BACKUP_DATABASE_AND_PRIVATE_OBJECTS"
            object_backup = backup_objects(source_storage, generation, objects, Path(directory))
            with dump.open("xb") as output:
                os.chmod(dump, 0o600)
                subprocess.run(
                    [
                        "docker",
                        "exec",
                        services.created["source-db"],
                        "pg_dump",
                        "-U",
                        "kasoma",
                        "-d",
                        database,
                        "--format=custom",
                        "--no-owner",
                        "--no-acl",
                    ],
                    stdout=output,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=120,
                )
            if inventory(source_engine) != before:
                raise ValueError("RECOVERY_SOURCE_CHANGED")
            stage = "STOP_OWNED_SOURCE_SERVICES"
            source_engine.dispose()
            services.stop("source-objects")
            services.stop("source-db")
            stage = "RESTORE_DATABASE_AND_PRIVATE_OBJECTS"
            started = monotonic()
            with dump.open("rb") as data:
                subprocess.run(
                    [
                        "docker",
                        "exec",
                        "-i",
                        services.created["destination-db"],
                        "pg_restore",
                        "-U",
                        "kasoma",
                        "-d",
                        database,
                        "--exit-on-error",
                        "--no-owner",
                        "--no-acl",
                    ],
                    stdin=data,
                    capture_output=True,
                    check=True,
                    timeout=120,
                )
            copied = restore_objects(
                destination_storage, generation, object_backup, Path(directory)
            )
            elapsed = round((monotonic() - started) * 1000)
        stage = "VERIFY_RESTORED_DATABASE_INVENTORY"
        if inventory(restored_engine) != before:
            raise ValueError("RECOVERY_DATABASE_MISMATCH")
        stage = "VERIFY_RESTORED_VECTOR"
        with restored_engine.connect() as right:
            if right.scalar(vector_query) != source_vector:
                raise ValueError("RECOVERY_VECTOR_MISMATCH")
        stage = "VERIFY_RESTORED_IMMUTABILITY"
        check_guards(restored_engine)
        stage = "VERIFY_RESTORED_RETIREMENT"
        verify_retirement_disabled(restored_engine)
        stage = "VERIFY_RESTORED_ENCRYPTED_ANSWER"
        verify_short_text(restored)
        stage = "VERIFY_RESTORED_PRESERVATION"
        verify_preservation(restored, expected_source_database=database)
        stage = "VERIFY_RESTORED_FROZEN_EXPORT"
        restored_export = StoredExport(
            target=fixture.target, frozen=fixture.frozen, storage=destination_storage
        )
        restored_export.verify(restored)
        stage = "VERIFY_PRIVATE_OBJECT_FAILURES"
        verify_faults(restored, restored_export, generation, objects[0])
        if inventory(restored_engine) != before:
            raise ValueError("RECOVERY_EVIDENCE_MUTATED")
        result.update(
            status="PASSED",
            tables=len(before),
            rows=sum(count for count, _ in before.values()),
            objects=len(objects),
            ciphertext_bytes=copied,
            restore_ms=elapsed,
            object_storage_recovery_verified=True,
            source_services_stopped_before_restore=True,
            same_storage_scope_verified=True,
            immutable_guards_verified=True,
            pgvector_verified=True,
            encrypted_evidence_verified=True,
            missing_corrupt_objects_rejected=True,
            stripped_retirement_execution_denied=True,
            production_rpo_rto_verified=False,
        )
    except Exception as error:
        # Child/SQL/provider exceptions can contain secrets or personal records.
        result.update(status="FAILED", failed_stage=stage)
        if isinstance(error, RecoveryCommandError):
            result["failure_kind"] = error.kind
    finally:
        connection_cleanup_failed = False
        for engine in engines:
            try:
                engine.dispose()
            except Exception:
                connection_cleanup_failed = True
        failed = services.cleanup()
        if connection_cleanup_failed:
            failed.append("OWNED_CONNECTION_DISPOSAL")
        result["cleanup_failed"] = failed
        if failed:
            result["status"] = "FAILED"
    return result


def main() -> None:
    try:
        result = drill(Settings())
    except Exception:
        result = {"status": "FAILED", "reason": "LOCAL_PROFILE_OR_DEPENDENCY_UNAVAILABLE"}
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
