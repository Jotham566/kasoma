"""NFR-MNT-001/NFR-SEC-002: only fresh synthetic load resources may be cleaned."""

from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from scripts import objective_load as load
from scripts.recovery_drill import local_database_url
from services.config import Settings
from services.export_retirement_install import owner_name

pytestmark = pytest.mark.integration


@pytest.fixture
def load_admin():
    config = Settings(app_env="development")
    url = local_database_url(config)
    engine = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", hide_parameters=True
    )
    try:
        yield config, engine
    finally:
        engine.dispose()


@pytest.mark.parametrize("history_mixed", [False, True])
def test_actual_load_migration_disposes_fresh_database_and_derived_owner(
    load_admin, monkeypatch, history_mixed
):
    config, admin = load_admin
    captured = []

    def stop_before_learner_fixtures(identity, mixed):
        assert mixed is history_mixed
        name = make_url(identity.settings.database_url.get_secret_value()).database
        assert load.database_name(name) == name
        role = owner_name(name, "public")
        captured.append((name, role))
        with identity.engine.connect() as db:
            assert db.scalar(text("SELECT version_num FROM alembic_version")) == "0042"
            assert (
                db.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"),
                    {"role": role},
                )
                is True
            )
        raise RuntimeError("Intentional synthetic fixture stop")

    monkeypatch.setattr(load, "populate", stop_before_learner_fixtures)
    result = load.run(config, history_mixed=history_mixed)
    assert result["status"] == "FAILED"
    assert result["failed_stage"] == "SYNTHETIC_FIXTURES"
    assert result["cleanup_failed"] is False
    assert len(captured) == 1
    name, role = captured[0]
    with admin.connect() as db:
        assert (
            db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=:name)"), {"name": name}
            )
            is False
        )
        assert (
            db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"), {"role": role}
            )
            is False
        )
    assert name not in str(result) and role not in str(result)


@pytest.mark.parametrize(
    "unsafe",
    [
        "LOGIN",
        "SUPERUSER",
        "CREATEDB",
        "CREATEROLE",
        "INHERIT",
        "REPLICATION",
        "BYPASSRLS",
        "MEMBER",
        "RECIPIENT",
    ],
)
def test_actual_unsafe_or_shared_owner_is_preserved(load_admin, unsafe):
    _, admin = load_admin
    name = load.database_name("kasoma_load_" + uuid4().hex)
    role = owner_name(name, "public")
    peer = role.replace("kasoma_er_", "kasoma_lp_", 1)
    created = []
    try:
        with admin.connect() as db:
            db.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOINHERIT'))
            created.append(role)
            if unsafe in {"MEMBER", "RECIPIENT"}:
                db.execute(text(f'CREATE ROLE "{peer}" NOLOGIN NOINHERIT'))
                created.append(peer)
                member, granted = (role, peer) if unsafe == "MEMBER" else (peer, role)
                db.execute(text(f'GRANT "{granted}" TO "{member}"'))
            else:
                # The flag is from the fixed parametrization above, never caller input.
                db.execute(text(f'ALTER ROLE "{role}" {unsafe}'))
        with pytest.raises(RuntimeError, match="Isolated owner cleanup refused"):
            load.cleanup_owner(admin, name)
        with admin.connect() as db:
            assert (
                db.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"),
                    {"role": role},
                )
                is True
            )
    finally:
        # Fixture teardown only: these exact roles were exclusively created by this test.
        for owned in reversed(created):
            with admin.connect() as db:
                db.execute(text(f'DROP ROLE "{owned}"'))


def test_postgresql_dependency_refusal_is_preserved(load_admin):
    _, admin = load_admin
    name = load.database_name("kasoma_load_" + uuid4().hex)
    role = owner_name(name, "public")
    database_created = role_created = False
    try:
        with admin.connect() as db:
            db.execute(text(f'CREATE DATABASE "{name}"'))
            database_created = True
            db.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOINHERIT'))
            role_created = True
            db.execute(text(f'GRANT CONNECT ON DATABASE "{name}" TO "{role}"'))
        with pytest.raises(DBAPIError):
            load.cleanup_owner(admin, name)
        with admin.connect() as db:
            assert (
                db.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"),
                    {"role": role},
                )
                is True
            )
    finally:
        if database_created:
            with admin.connect() as db:
                db.execute(text(f'DROP DATABASE "{name}"'))
        if role_created:
            load.cleanup_owner(admin, name)
