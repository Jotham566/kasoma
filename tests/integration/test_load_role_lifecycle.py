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
            oid = db.scalar(text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role})
            if unsafe in {"MEMBER", "RECIPIENT"}:
                db.execute(text(f'CREATE ROLE "{peer}" NOLOGIN NOINHERIT'))
                created.append(peer)
                member, granted = (role, peer) if unsafe == "MEMBER" else (peer, role)
                db.execute(text(f'GRANT "{granted}" TO "{member}"'))
            else:
                # The flag is from the fixed parametrization above, never caller input.
                db.execute(text(f'ALTER ROLE "{role}" {unsafe}'))
        with pytest.raises(RuntimeError, match="Isolated owner cleanup refused"):
            load.cleanup_owner(admin, name, oid)
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
            oid = db.scalar(text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role})
            db.execute(text(f'GRANT CONNECT ON DATABASE "{name}" TO "{role}"'))
        with pytest.raises(DBAPIError):
            load.cleanup_owner(admin, name, oid)
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
            load.cleanup_owner(admin, name, oid)


def test_role_created_between_absence_check_and_migration_is_not_owned(load_admin, monkeypatch):
    from sqlalchemy import event

    config, control = load_admin
    original = load.create_engine
    names = []
    fixture_roles = []

    def race(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith('CREATE DATABASE "'):
            names.append(load.database_name(statement.split('"')[1]))
        if "SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_roles WHERE rolname=" in statement:
            assert len(names) == 1 and not fixture_roles
            role = owner_name(names[0], "public")
            # This separate creator commits after the absence SELECT has executed.
            with control.connect() as db:
                db.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOINHERIT'))
                fixture_roles.append(role)

    def intercepted(*args, **kwargs):
        engine = original(*args, **kwargs)
        event.listen(engine, "after_cursor_execute", race)
        return engine

    def stop_before_learner_fixtures(*args):
        raise RuntimeError("Intentional synthetic fixture stop")

    monkeypatch.setattr(load, "create_engine", intercepted)
    monkeypatch.setattr(load, "populate", stop_before_learner_fixtures)
    try:
        result = load.run(config)
        assert len(fixture_roles) == 1
        role = fixture_roles[0]
        with control.connect() as db:
            assert (
                db.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"),
                    {"role": role},
                )
                is True
            )
        assert result["status"] == "FAILED"
        assert result["failed_stage"] == "CREATE_OWNER_ROLE"
        assert result["cleanup_failed"] is False
    finally:
        # Only this test's independently created role; never an application role.
        for role in fixture_roles:
            with control.connect() as db:
                if db.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"),
                    {"role": role},
                ):
                    db.execute(text(f'DROP ROLE "{role}"'))


def test_replacement_role_identity_is_preserved(load_admin):
    _, admin = load_admin
    name = load.database_name("kasoma_load_" + uuid4().hex)
    role = owner_name(name, "public")
    oid = load.create_owner(admin, name)
    replacement = None
    try:
        with admin.connect() as db:
            db.execute(text(f'DROP ROLE "{role}"'))
            db.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOINHERIT'))
            replacement = db.scalar(
                text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role}
            )
        assert replacement != oid
        with pytest.raises(RuntimeError, match="Isolated owner cleanup refused"):
            load.cleanup_owner(admin, name, oid)
        with admin.connect() as db:
            assert (
                db.scalar(text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role})
                == replacement
            )
    finally:
        load.cleanup_owner(admin, name, replacement if replacement is not None else oid)
