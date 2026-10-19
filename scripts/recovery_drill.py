"""NFR-REL-002: isolated synthetic logical restore, never the developer database."""

import hashlib
import json
import os
import re
import subprocess
import tempfile
import traceback
from pathlib import Path
from time import monotonic
from uuid import uuid4

from pydantic import SecretStr
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DBAPIError

from scripts.recovery_channel_preservation import verify_preservation
from scripts.recovery_fixture import populate
from scripts.recovery_short_text import verify_short_text
from services.config import Settings
from services.domain.assessment import Attempt, Grade
from services.domain.content import ItemVersion
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.domain.grading_audits import (
    GradingAuditAssignment,
    GradingAuditReview,
    GradingPublication,
    GradingPublicationCounter,
    GradingReviewCounter,
)
from services.domain.identity import Consent
from services.domain.mastery import MasteryEvidence
from services.identity import IdentityError, IdentityService
from services.providers import FakeMessagingProvider


def validate_name(name: str) -> str:
    if not re.fullmatch(r"kasoma_drill_(src|dst)_[0-9a-f]{32}", name):
        raise ValueError("Only generated recovery database names are allowed")
    return name


def local_database_url(settings: Settings) -> URL:
    url = make_url(settings.database_url.get_secret_value())
    if (
        settings.app_env != "development"
        or url.drivername != "postgresql+psycopg"
        or url.host not in {"localhost", "127.0.0.1"}
        or url.port != 55432
        or url.username != "kasoma"
        or url.query
    ):
        raise ValueError("Recovery drill requires the standard local Compose development profile")
    return url


def inventory(engine: Engine) -> dict[str, tuple[int, str]]:
    result = {}
    with engine.connect() as db:
        for table in sorted(inspect(engine).get_table_names(schema="public")):
            quoted = engine.dialect.identifier_preparer.quote(table)
            rows = db.scalars(text(f"SELECT to_jsonb(t)::text FROM public.{quoted} t ORDER BY 1"))
            digest, count = hashlib.sha256(), 0
            for row in rows:
                digest.update(row.encode())
                digest.update(b"\n")
                count += 1
            result[table] = (count, digest.hexdigest())
    return result


def check_guards(engine: Engine) -> None:
    for statement in (
        "UPDATE channel_preservation_snapshots SET source_version=source_version",
        "UPDATE channel_preservation_bodies SET encrypted_payload=encrypted_payload",
        "DELETE FROM channel_preservation_bodies",
        "DELETE FROM channel_preservation_disposals",
        "DELETE FROM outbound_messages",
        "UPDATE data_request_receipts SET id=gen_random_uuid()",
        "DELETE FROM data_request_receipts WHERE id IN (SELECT record_id FROM legal_holds "
        "WHERE record_type='DATA_REQUEST_RECEIPT')",
        "UPDATE inbound_messages SET command='STOP'",
        "UPDATE outbound_messages SET recipient_hash='synthetic-tampering'",
        "UPDATE attempts SET channel = 'WHATSAPP'",
        "UPDATE assessment_grading_history SET snapshot=snapshot",
        "UPDATE grading_bands SET held_out_exact=held_out_exact",
        "UPDATE grading_band_history SET snapshot=snapshot",
        "UPDATE grading_publications SET ordinal=ordinal",
        "UPDATE grading_audit_assignments SET assigned_at=assigned_at",
        "UPDATE grading_audit_reviews SET criterion_points=criterion_points",
        "UPDATE grading_review_counters SET completed_audits=0",
        "UPDATE grading_publication_counters SET returned_grades=0,assigned_audits=0",
        "UPDATE topics t SET subject_id=(SELECT id FROM subjects WHERE id<>t.subject_id LIMIT 1) "
        "WHERE t.id IN (SELECT topic_id FROM grading_bands)",
        "UPDATE assessment_grading_work SET status='QUEUED',revision=revision+1",
        "UPDATE grades SET answer_specification_hash = 'synthetic-tampering'",
        "UPDATE item_versions SET document = '{}'::jsonb WHERE status = 'APPROVED'",
        "UPDATE personal_export_generations SET digest = repeat('0', 64)",
        "UPDATE personal_export_jobs SET status = 'QUEUED' WHERE status = 'READY'",
    ):
        rejected = False
        with engine.connect() as db:
            try:
                db.execute(text(statement))
            except DBAPIError:
                rejected = True
            finally:
                db.rollback()
        if not rejected:
            raise RuntimeError("Restored immutable evidence guard did not reject a mutation")


def drill(settings: Settings) -> dict[str, object]:
    url = local_database_url(settings)
    suffix = uuid4().hex
    source, destination = (
        validate_name(f"kasoma_drill_{kind}_{suffix}") for kind in ("src", "dst")
    )
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", hide_parameters=True
    )
    created: list[str] = []
    engines: list[Engine] = []
    cleanup_failed: list[str] = []
    result: dict[str, object] = {"status": "FAILED", "profile": "isolated-synthetic-logical-v1"}
    stage = "CREATE_ISOLATED_DATABASES"
    try:
        # No source override exists: only databases created here may be dumped/restored/dropped.
        with admin.connect() as db:
            for name in (source, destination):
                db.execute(text(f'CREATE DATABASE "{name}"'))
                created.append(name)
        source_url, destination_url = url.set(database=source), url.set(database=destination)
        stage = "MIGRATE_SYNTHETIC_SOURCE"
        env = dict(os.environ, DATABASE_URL=source_url.render_as_string(hide_password=False))
        subprocess.run(["make", "migrate"], env=env, capture_output=True, check=True, timeout=120)
        synthetic = settings.model_copy(
            update={
                "database_url": SecretStr(source_url.render_as_string(hide_password=False)),
                "model_provider": "fake",
                "email_provider": "fake",
                "sms_provider": "fake",
            }
        )
        stage = "POPULATE_SYNTHETIC_SOURCE"
        export = populate(synthetic)
        source_engine, restored_engine = (
            create_engine(value, hide_parameters=True) for value in (source_url, destination_url)
        )
        engines.extend([source_engine, restored_engine])
        stage = "CAPTURE_INVENTORY"
        before = inventory(source_engine)
        for model in (
            Attempt,
            Grade,
            MasteryEvidence,
            Consent,
            ItemVersion,
            ExportJob,
            ExportGeneration,
            GradingPublication,
            GradingAuditAssignment,
            GradingAuditReview,
            GradingPublicationCounter,
            GradingReviewCounter,
        ):
            if before.get(model.__tablename__, (0, ""))[0] == 0:
                raise RuntimeError("Synthetic evidence fixture is incomplete")
        Path(".local").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="recovery-", dir=".local") as directory:
            dump = Path(directory) / "synthetic.dump"
            stage = "BACKUP_SYNTHETIC_SOURCE"
            with dump.open("xb") as output:
                os.chmod(dump, 0o600)
                subprocess.run(
                    [
                        "docker",
                        "compose",
                        "exec",
                        "-T",
                        "postgres",
                        "pg_dump",
                        "-U",
                        "kasoma",
                        "-d",
                        source,
                        "--format=custom",
                        "--no-owner",
                        "--no-acl",
                    ],
                    stdout=output,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=120,
                )
            started = monotonic()
            stage = "RESTORE_FRESH_DESTINATION"
            with dump.open("rb") as data:
                subprocess.run(
                    [
                        "docker",
                        "compose",
                        "exec",
                        "-T",
                        "postgres",
                        "pg_restore",
                        "-U",
                        "kasoma",
                        "-d",
                        destination,
                        "--exit-on-error",
                        "--no-owner",
                        "--no-acl",
                    ],
                    stdin=data,
                    capture_output=True,
                    check=True,
                    timeout=120,
                )
            elapsed_ms = round((monotonic() - started) * 1000)
        stage = "VERIFY_RESTORED_EVIDENCE"
        if inventory(restored_engine) != before:
            raise RuntimeError("Restored row inventory mismatch")
        with source_engine.connect() as original, restored_engine.connect() as restored:
            extension = text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            source_vector = original.scalar(extension)
            if not source_vector or restored.scalar(extension) != source_vector:
                raise RuntimeError("Restored pgvector extension mismatch")
        with restored_engine.connect() as restored:
            if (
                restored.scalar(text("SELECT to_regclass('public.ix_audit_activity_window')"))
                is None
            ):
                raise RuntimeError("Restored audit activity index is missing")
        check_guards(restored_engine)
        stage = "VERIFY_RESTORED_EXPORT"
        fake = FakeMessagingProvider()
        restored_settings = synthetic.model_copy(
            update={
                "database_url": SecretStr(destination_url.render_as_string(hide_password=False))
            }
        )
        restored_identity = IdentityService(restored_engine, restored_settings, fake, fake)
        export.verify(restored_identity)
        verify_short_text(restored_identity)
        verify_preservation(restored_identity)
        if inventory(restored_engine) != before or inventory(source_engine) != before:
            raise RuntimeError("Recovery verification changed evidence")
        result.update(
            status="PASSED",
            restore_ms=elapsed_ms,
            tables=len(before),
            rows=sum(count for count, _ in before.values()),
            immutable_guards_verified=True,
            pgvector_verified=True,
            populated_export_verified=True,
            exact_export_receipt_hold_verified=True,
            encrypted_short_text_verified=True,
            encrypted_channel_preservation_verified=True,
            object_storage_recovery_verified=False,
            production_rpo_rto_verified=False,
        )
    except Exception as error:
        # Do not print connection strings, child output, fixture records or DB diagnostics.
        result.update(status="FAILED", failed_stage=stage)
        result["failure_kind"] = (
            "IDENTITY_POLICY"
            if isinstance(error, IdentityError)
            else "DATABASE_INVARIANT"
            if isinstance(error, DBAPIError)
            else "FIXTURE_CONTRACT"
            if isinstance(error, ValueError)
            else "UNEXPECTED"
        )
        root = Path(__file__).resolve().parents[1]
        result["failure_sites"] = [
            f"{Path(frame.filename).name}:{frame.lineno}"
            for frame in traceback.extract_tb(error.__traceback__)
            if Path(frame.filename).resolve().is_relative_to(root)
        ][-3:]
    finally:
        for engine in engines:
            engine.dispose()
        for name in reversed(created):
            try:
                with admin.connect() as db:
                    db.execute(text(f'DROP DATABASE "{validate_name(name)}"'))
            except Exception:
                cleanup_failed.append(name)
        admin.dispose()
    result["cleanup_failed"] = cleanup_failed
    if cleanup_failed:
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
