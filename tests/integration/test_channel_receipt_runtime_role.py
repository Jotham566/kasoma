"""Receipt hold creation/release under a real restricted login; assessment grants stay unchanged."""

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
from tests.integration.test_channel_receipt_holds import receipt, scoped
from tests.integration.test_legal_holds import prepare

pytestmark = pytest.mark.integration


def test_channel_holds_use_restricted_login_without_payload_or_schema_rewrite(
    content, caplog, capsys
):
    owner, client, actors, *_ = content
    target, body = prepare(content)
    incoming, outgoing = receipt(content)
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
                for table in ["data_subject_requests", "inbound_messages", "outbound_messages"]:
                    db.execute(text(f"GRANT UPDATE(id) ON {qs}.{quote(table)} TO {qr}"))
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
                "channel_receipt_holds_enabled": True,
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
        for kind, source in [
            ("CHANNEL_INBOUND_RECEIPT", incoming),
            ("CHANNEL_OUTBOUND_RECEIPT", outgoing),
        ]:
            value = HoldInput.model_validate(scoped(body, kind, source))
            key = uuid4()
            held = service.create(token, UUID(target), value, key, uuid4())
            assert held.record_id == source
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
            f"UPDATE {qs}.outbound_messages SET recipient_hash='tampered'",
            f"UPDATE {qs}.inbound_messages SET sender_encrypted='tampered'",
            f"DELETE FROM {qs}.outbound_messages",
            f"DELETE FROM {qs}.legal_holds",
            f"UPDATE {qs}.user_roles SET role='ADMIN'",
        ]:
            with restricted.connect() as db, pytest.raises(DBAPIError) as rejected:
                db.execute(text(statement))
            assert rejected.value.orig.sqlstate == "42501"
        for table in ["inbound_messages", "outbound_messages"]:
            with (
                restricted.connect() as db,
                pytest.raises(DBAPIError, match="Channel receipt identity is immutable"),
            ):
                db.execute(text(f"UPDATE {qs}.{quote(table)} SET id=gen_random_uuid()"))
        assert password not in caplog.text + capsys.readouterr().out
    finally:
        if restricted is not None:
            restricted.dispose()
        if created:
            with owner.engine.begin() as db:
                for table in ["data_subject_requests", "inbound_messages", "outbound_messages"]:
                    db.execute(text(f"REVOKE UPDATE(id) ON {qs}.{quote(table)} FROM {qr}"))
                db.execute(text(f"REVOKE ALL ON ALL TABLES IN SCHEMA {qs} FROM {qr}"))
                db.execute(text(f"REVOKE ALL ON SCHEMA {qs} FROM {qr}"))
                db.execute(text(f"DROP ROLE {qr}"))
    with owner.engine.connect() as db:
        assert (
            db.scalar(text("SELECT count(*) FROM pg_roles WHERE rolname=:role"), {"role": role})
            == 0
        )
