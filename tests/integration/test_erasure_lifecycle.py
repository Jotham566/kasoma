"""ADR-061 dormant persistence: actual SQL must not grant closure or erasure."""

import os
import subprocess
from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.identity import User
from services.erasure_inventory import check_source_shape
from services.identity_contracts import OTPRequest, OTPVerify

pytestmark = pytest.mark.integration


def assert_denied(engine, statement, parameters=None):
    with pytest.raises(DBAPIError) as rejected, engine.begin() as db:
        db.execute(text(statement), parameters or {})
    assert rejected.value.orig.sqlstate == "42501"


def test_dormant_state_has_database_identity_and_no_authority(identity):
    service, *_ = identity
    with service.engine.connect() as db:
        row = db.execute(
            text("""
          SELECT s.*,d.oid AS actual_database,n.oid AS actual_namespace,
            clock_timestamp() AS observed
          FROM account_erasure_state s CROSS JOIN pg_catalog.pg_database d
          CROSS JOIN pg_catalog.pg_namespace n
          WHERE d.datname=current_database() AND n.nspname=current_schema()
        """)
        ).one()
        assert row.singleton == 1
        assert row.database_oid == row.actual_database
        assert row.namespace_oid == row.actual_namespace
        assert not row.original_scope_eligible
        assert not row.creation_enabled and not row.execution_enabled
        assert row.owner_oid is None and row.executor_oid is None
        assert row.scope_nonce is not None
        assert row.installed_at <= row.observed
        assert row.policy == "synthetic-account-erasure-v1"
        assert row.manifest == "erasure-0045-v1"
        assert db.scalar(text("SELECT count(*) FROM account_erasure_plans")) == 0
        assert db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) == 0
        check_source_shape(db)
        # No PUBLIC grants and no SECURITY DEFINER execution capability were added.
        assert (
            db.scalar(
                text("""
          SELECT count(*) FROM pg_catalog.pg_class c,
            LATERAL aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) a
          WHERE c.relnamespace=to_regnamespace(current_schema())
            AND c.relname LIKE 'account_erasure_%' AND a.grantee=0
        """)
            )
            == 0
        )
        assert (
            db.scalar(
                text("""
          SELECT count(*) FROM pg_catalog.pg_proc p,
            LATERAL aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a
          WHERE p.pronamespace=to_regnamespace(current_schema())
            AND p.proname LIKE 'account_erasure_%' AND (p.prosecdef OR a.grantee=0)
        """)
            )
            == 0
        )


def test_even_migration_role_cannot_activate_or_forge_execution(identity):
    service, *_ = identity
    for change in [
        "creation_enabled=true",
        "execution_enabled=true",
        "original_scope_eligible=true",
        "owner_oid=10",
        "executor_oid=10",
        "scope_nonce=gen_random_uuid()",
        "installed_at=clock_timestamp()-interval '6 years'",
        "manifest='erasure-0044-v1'",
    ]:
        assert_denied(service.engine, "UPDATE account_erasure_state SET " + change)
    assert_denied(service.engine, "DELETE FROM account_erasure_state")
    for table in ["account_erasure_state", "account_erasure_plans", "account_erasure_jobs"]:
        # BEFORE INSERT denies even a structurally incomplete fabricated row.
        assert_denied(service.engine, f"INSERT INTO {table} DEFAULT VALUES")
        assert_denied(service.engine, f"TRUNCATE {table}")
    with service.engine.connect() as db:
        assert db.scalar(text("SELECT count(*) FROM account_erasure_state")) == 1
        assert db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) == 0


def test_direct_closure_denied_without_disrupting_existing_identity(identity):
    service, _, _, _ = identity
    email = "dormant-closure@example.invalid"
    challenge = service.request_otp(OTPRequest(identifier=email, device_id=uuid4()), "test", None)
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    subject = service.me(credentials.access_token).id
    for statement in [
        "UPDATE users SET closed_at=clock_timestamp() WHERE id=:subject",
        "UPDATE users SET status='DISABLED',closed_at=clock_timestamp() WHERE id=:subject",
        "INSERT INTO users(id,status,created_at,closed_at) "
        "VALUES(gen_random_uuid(),'DISABLED',clock_timestamp(),clock_timestamp())",
    ]:
        assert_denied(service.engine, statement, {"subject": subject})
    assert service.me(credentials.access_token).id == subject
    with service.engine.begin() as db:
        # Existing administrative DISABLED is not backdated or reclassified as closure.
        db.execute(
            text("UPDATE users SET status='DISABLED' WHERE id=:subject"), {"subject": subject}
        )
    with Session(service.engine) as db:
        user = db.get(User, subject)
        assert user.status == "DISABLED" and user.closed_at is None
        assert db.scalar(select(User.closed_at).where(User.id == subject)) is None


@pytest.mark.parametrize("identity", ["0044"], indirect=True)
def test_additive0045_preserves_populated0044_identity_and_repeated_upgrade(identity):
    service, *_ = identity
    challenge = service.request_otp(
        OTPRequest(identifier="pre0045@example.invalid", device_id=uuid4()), "test", None
    )
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    subject = service.me(credentials.access_token).id
    with service.engine.connect() as db:
        before = tuple(db.execute(text("SELECT id,status,created_at FROM users")).one())
        before_counts = tuple(
            db.execute(
                text("""
          SELECT (SELECT count(*) FROM auth_sessions),(SELECT count(*) FROM user_identifiers),
            (SELECT count(*) FROM audit_log),(SELECT count(*) FROM data_subject_requests)
        """)
            ).one()
        )
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            env=os.environ | {"DATABASE_URL": service.settings.database_url.get_secret_value()},
            check=True,
            capture_output=True,
        )
    with service.engine.connect() as db:
        assert tuple(db.execute(text("SELECT id,status,created_at FROM users")).one()) == before
        assert (
            tuple(
                db.execute(
                    text("""
          SELECT (SELECT count(*) FROM auth_sessions),(SELECT count(*) FROM user_identifiers),
            (SELECT count(*) FROM audit_log),(SELECT count(*) FROM data_subject_requests)
        """)
                ).one()
            )
            == before_counts
        )
        assert db.scalar(
            text("SELECT closed_at IS NULL FROM users WHERE id=:subject"), {"subject": subject}
        )
        check_source_shape(db)
    assert service.me(credentials.access_token).id == subject
