"""ADR-057 real restricted login: capture needs no source-payload write or DDL rights."""

import secrets
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.channel_preservation import ChannelPreservationService
from services.channel_preservation_contracts import PreservationCapture, PreservationSource
from services.database import engine_for
from services.domain.messaging import ConversationState, OutboundMessage
from services.identity import IdentityService
from services.legal_hold_contracts import HoldRelease
from services.legal_holds import LegalHoldService
from services.providers import FakeMessagingProvider
from tests.integration.test_channel_preservation import prepared_capture

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("kind", ["CHANNEL_LINK_SNAPSHOT", "CHANNEL_CONVERSATION_SNAPSHOT"])
def test_capture_and_release_use_actual_restricted_database_login(content, caplog, capsys, kind):
    owner, _, actors, *_ = content
    target, source, decision, learner = prepared_capture(content)
    if kind == "CHANNEL_CONVERSATION_SNAPSHOT":
        from services.legal_holds import database_now
        from tests.integration.test_channel_receipt_holds import receipt

        _, outgoing = receipt(content)
        with Session(owner.engine) as db, db.begin():
            message = db.get(OutboundMessage, outgoing)
            message.link_id, message.link_revision = UUID(source["source_link_id"]), 1
            now = database_now(db)
            db.add(
                ConversationState(
                    link_id=message.link_id,
                    actor_id=learner,
                    link_revision=1,
                    session_id=None,
                    expected_outbound_id=outgoing,
                    updated_at=now,
                    expires_at=now + timedelta(hours=24),
                )
            )
        source["source_kind"] = kind
    with owner.engine.connect() as db:
        schema = db.scalar(text("SELECT current_schema()"))
    role = "kasoma_snapshot_test_" + uuid4().hex
    password = secrets.token_urlsafe(32)
    quote = owner.engine.dialect.identifier_preparer.quote
    qr, qs = quote(role), quote(schema)
    locks = [
        ("data_subject_requests", "id"),
        ("channel_links", "id"),
        ("channel_senders", "sender_hash"),
        ("conversation_states", "link_id"),
        ("outbound_messages", "id"),
        ("channel_preservation_bodies", "snapshot_id"),
    ]
    created, restricted = False, None
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
            for table, rights in [
                ("identity_rate_buckets", "INSERT, UPDATE"),
                ("legal_holds", "INSERT, UPDATE"),
                ("legal_hold_receipts", "INSERT"),
                ("audit_log", "INSERT"),
                ("identity_outbox_events", "INSERT"),
                ("channel_preservation_snapshots", "INSERT"),
                ("channel_preservation_bodies", "INSERT"),
            ]:
                db.execute(text(f"GRANT {rights} ON {qs}.{quote(table)} TO {qr}"))
            for table, column in locks:
                db.execute(text(f"GRANT UPDATE({quote(column)}) ON {qs}.{quote(table)} TO {qr}"))
        url = make_url(owner.settings.database_url.get_secret_value()).set(
            username=role, password=password
        )
        settings = owner.settings.model_copy(
            update={
                "database_url": SecretStr(url.render_as_string(hide_password=False)),
                "channel_preservation_enabled": True,
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
        service = ChannelPreservationService(identity)
        token = actors["admin"]["Authorization"].removeprefix("Bearer ")
        selection = service.inspect(
            token, UUID(target), PreservationSource.model_validate(source), uuid4()
        )
        body = PreservationCapture.model_validate(source | selection.model_dump() | decision)
        key = uuid4()
        captured = service.capture(token, UUID(target), body, key, uuid4())
        assert service.capture(token, UUID(target), body, key, uuid4()).id == captured.id
        settings.channel_preservation_enabled = False
        released = LegalHoldService(identity).release(
            token,
            UUID(target),
            captured.id,
            HoldRelease(decision_reference=uuid4(), affirmative=True),
            uuid4(),
            uuid4(),
        )
        assert released.status == "RELEASED"
        for statement in [
            f"CREATE TABLE {qs}.unauthorized_snapshot_copy(id int)",
            f"UPDATE {qs}.channel_links SET external_identifier_encrypted='tampered'",
            f"UPDATE {qs}.channel_senders SET barrier_at=NULL",
            f"UPDATE {qs}.conversation_states SET state_version=1",
            f"UPDATE {qs}.channel_preservation_bodies SET encrypted_payload='tampered'",
            f"DELETE FROM {qs}.channel_preservation_bodies",
            f"UPDATE {qs}.channel_preservation_snapshots SET captured_at=clock_timestamp()",
            f"DELETE FROM {qs}.legal_holds",
            f"UPDATE {qs}.user_roles SET role='ADMIN'",
        ]:
            with pytest.raises(DBAPIError) as error, restricted.begin() as db:
                db.execute(text(statement))
            assert error.value.orig.sqlstate == "42501"
        with pytest.raises(DBAPIError, match="immutable"), restricted.begin() as db:
            db.execute(text(f"UPDATE {qs}.channel_preservation_bodies SET snapshot_id=snapshot_id"))
        assert password not in caplog.text + capsys.readouterr().out
    finally:
        if restricted is not None:
            restricted.dispose()
        if created:
            with owner.engine.begin() as db:
                for table, column in locks:
                    db.execute(
                        text(f"REVOKE UPDATE({quote(column)}) ON {qs}.{quote(table)} FROM {qr}")
                    )
                db.execute(text(f"REVOKE ALL ON ALL TABLES IN SCHEMA {qs} FROM {qr}"))
                db.execute(text(f"REVOKE ALL ON SCHEMA {qs} FROM {qr}"))
                db.execute(text(f"DROP ROLE {qr}"))
    with owner.engine.connect() as db:
        assert (
            db.scalar(text("SELECT count(*) FROM pg_roles WHERE rolname=:role"), {"role": role})
            == 0
        )
