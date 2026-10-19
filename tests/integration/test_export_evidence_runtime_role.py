"""Export hold creation/release under a real restricted login; assessment grants stay unchanged."""

import secrets
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from services.database import engine_for
from services.identity import IdentityService
from services.legal_hold_contracts import HoldInput, HoldRelease
from services.legal_holds import LegalHoldService
from services.providers import FakeMessagingProvider
from tests.integration.test_export_evidence_holds import clear_job, sources

pytestmark = pytest.mark.integration


def test_export_holds_use_actual_restricted_login_without_retirement_permission(
    content, caplog, capsys
):
    owner, client, actors, *_ = content
    target, body, source = sources(content)
    clear_job(content, source)
    with owner.engine.connect() as db:
        schema = db.scalar(text("SELECT current_schema()"))
    role = "kasoma_privacy_test_" + uuid4().hex
    password = secrets.token_urlsafe(32)
    quote = owner.engine.dialect.identifier_preparer.quote
    qr, qs = quote(role), quote(schema)
    created, restricted = False, None
    try:
        try:
            with owner.engine.begin() as db:
                db.execute(
                    text("SELECT set_config('kasoma.test_role_password',:value,true)"),
                    {"value": password},
                )
                db.execute(
                    text(f"""DO $$ BEGIN
                  EXECUTE format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
                    NOINHERIT NOBYPASSRLS PASSWORD %L','{role}',
                    current_setting('kasoma.test_role_password'));
                END $$""")
                )
            created = True
            with owner.engine.begin() as db:
                db.execute(text(f"GRANT USAGE ON SCHEMA {qs} TO {qr}"))
                db.execute(text(f"GRANT SELECT ON ALL TABLES IN SCHEMA {qs} TO {qr}"))
                for table, grants in [
                    ("identity_rate_buckets", "INSERT, UPDATE"),
                    ("legal_holds", "INSERT, UPDATE"),
                    ("legal_hold_receipts", "INSERT"),
                    ("audit_log", "INSERT"),
                    ("identity_outbox_events", "INSERT"),
                ]:
                    db.execute(text(f"GRANT {grants} ON {qs}.{quote(table)} TO {qr}"))
                for table in ["data_subject_requests", "data_request_receipts"]:
                    db.execute(text(f"GRANT UPDATE(id) ON {qs}.{quote(table)} TO {qr}"))
                db.execute(text(f"GRANT UPDATE(request_id) ON {qs}.personal_export_jobs TO {qr}"))
        except DBAPIError:
            raise RuntimeError(
                "Restricted privacy provisioning failed; diagnostics withheld"
            ) from None
        url = make_url(owner.settings.database_url.get_secret_value()).set(
            username=role, password=password
        )
        settings = owner.settings.model_copy(
            update={
                "database_url": SecretStr(url.render_as_string(hide_password=False)),
                "export_evidence_holds_enabled": True,
            }
        )
        restricted = engine_for(settings)
        with restricted.connect() as db:
            assert db.scalar(text("SELECT current_user")) == role
            assert db.execute(
                text(
                    "SELECT rolsuper,rolcreatedb,rolcreaterole,rolbypassrls "
                    "FROM pg_roles WHERE rolname=current_user"
                )
            ).one() == (False, False, False, False)
        fake = FakeMessagingProvider()
        identity = IdentityService(restricted, settings, fake, fake, owner.clock)
        service = LegalHoldService(identity)
        token = actors["admin"]["Authorization"].removeprefix("Bearer ")
        refs = service.export_sources(token, UUID(target), UUID(source), None, 50, uuid4())
        for kind, record in [
            ("DATA_REQUEST_RECEIPT", refs.receipt_ids[0]),
            ("EXPORT_JOB_RECEIPT", UUID(source)),
        ]:
            value = HoldInput.model_validate(body | {"record_type": kind, "record_id": record})
            key = uuid4()
            held = service.create(token, UUID(target), value, key, uuid4())
            assert held.record_id == record
            assert service.create(token, UUID(target), value, key, uuid4()).id == held.id
            assert (
                service.release(
                    token,
                    UUID(target),
                    held.id,
                    HoldRelease(decision_reference=uuid4(), affirmative=True),
                    uuid4(),
                    uuid4(),
                ).status
                == "RELEASED"
            )
        for statement in [
            f"CREATE TABLE {qs}.unauthorized_receipt_copy(id int)",
            f"UPDATE {qs}.data_request_receipts SET request_hash='tampered'",
            f"UPDATE {qs}.personal_export_jobs SET status='FAILED'",
            f"DELETE FROM {qs}.personal_export_jobs",
            f"DELETE FROM {qs}.legal_holds",
            f"UPDATE {qs}.user_roles SET role='ADMIN'",
        ]:
            with restricted.connect() as db, pytest.raises(DBAPIError) as rejected:
                db.execute(text(statement))
            assert rejected.value.orig.sqlstate == "42501"
        for table in ["data_subject_requests", "data_request_receipts"]:
            with (
                restricted.connect() as db,
                pytest.raises(DBAPIError, match="Invalid export completion|append-only"),
            ):
                db.execute(text(f"UPDATE {qs}.{quote(table)} SET id=gen_random_uuid()"))
        assert password not in caplog.text + capsys.readouterr().out
    finally:
        if restricted is not None:
            restricted.dispose()
        if created:
            with owner.engine.begin() as db:
                for table in ["data_subject_requests", "data_request_receipts"]:
                    db.execute(text(f"REVOKE UPDATE(id) ON {qs}.{quote(table)} FROM {qr}"))
                db.execute(
                    text(f"REVOKE UPDATE(request_id) ON {qs}.personal_export_jobs FROM {qr}")
                )
                db.execute(text(f"REVOKE ALL ON ALL TABLES IN SCHEMA {qs} FROM {qr}"))
                db.execute(text(f"REVOKE ALL ON SCHEMA {qs} FROM {qr}"))
                db.execute(text(f"DROP ROLE {qr}"))
    with owner.engine.connect() as db:
        assert (
            db.scalar(text("SELECT count(*) FROM pg_roles WHERE rolname=:role"), {"role": role})
            == 0
        )
