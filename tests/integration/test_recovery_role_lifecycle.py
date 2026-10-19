"""NFR-SEC-002/NFR-MNT-001: recovery cannot adopt unrelated cluster roles."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from scripts import recovery_drill as recovery
from services.config import Settings
from services.export_retirement_install import owner_name

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("kind", ["src", "dst"])
def test_preexisting_derived_role_is_not_recovery_cleanup_authority(monkeypatch, kind):
    config = Settings(app_env="development")
    admin = create_engine(
        recovery.local_database_url(config).set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        hide_parameters=True,
    )
    suffix = uuid4()
    name = recovery.validate_name(f"kasoma_drill_{kind}_{suffix.hex}")
    role = owner_name(name, "public")
    owned = False
    try:
        with admin.connect() as db:
            db.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOINHERIT'))
            owned = True
            original = db.scalar(
                text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role}
            )
        monkeypatch.setattr(recovery, "uuid4", lambda: suffix)
        monkeypatch.setattr(recovery.subprocess, "run", Mock())
        monkeypatch.setattr(
            recovery, "populate", Mock(side_effect=RuntimeError("Intentional fixture stop"))
        )
        result = recovery.drill(config)
        with admin.connect() as db:
            assert (
                db.scalar(text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role})
                == original
            )
            for target in ("src", "dst"):
                assert (
                    db.scalar(
                        text("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=:name)"),
                        {"name": f"kasoma_drill_{target}_{suffix.hex}"},
                    )
                    is False
                )
        assert result["status"] == "FAILED"
        assert result["cleanup_failed"] == []
        assert role not in str(result)
    finally:
        # Only the exact role exclusively created by this test, never another owner.
        if owned:
            with admin.connect() as db:
                db.execute(text(f'DROP ROLE IF EXISTS "{role}"'))
        admin.dispose()


def test_same_name_replacement_is_preserved_by_recovery_cleanup(monkeypatch):
    config = Settings(app_env="development")
    admin = create_engine(
        recovery.local_database_url(config).set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        hide_parameters=True,
    )
    suffix = uuid4()
    source = recovery.validate_name(f"kasoma_drill_src_{suffix.hex}")
    role = owner_name(source, "public")
    replacements = []

    def replace_before_fixture_stop(settings):
        # Migration is intentionally not run: this synthetic owner has no dependencies.
        with admin.connect() as db:
            original = db.scalar(
                text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role}
            )
            assert isinstance(original, int)
            db.execute(text(f'DROP ROLE "{role}"'))
            db.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOINHERIT'))
            replacement = db.scalar(
                text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role}
            )
            replacements.append(replacement)
            assert replacement != original
        raise RuntimeError("Intentional replacement fixture stop")

    monkeypatch.setattr(recovery, "uuid4", lambda: suffix)
    monkeypatch.setattr(recovery.subprocess, "run", Mock())
    monkeypatch.setattr(recovery, "populate", replace_before_fixture_stop)
    try:
        result = recovery.drill(config)
        assert len(replacements) == 1
        with admin.connect() as db:
            assert (
                db.scalar(text("SELECT oid FROM pg_roles WHERE rolname=:role"), {"role": role})
                == replacements[0]
            )
            for target in ("src", "dst"):
                assert (
                    db.scalar(
                        text("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=:name)"),
                        {"name": f"kasoma_drill_{target}_{suffix.hex}"},
                    )
                    is False
                )
        assert result["status"] == "FAILED"
        assert result["failed_stage"] == "POPULATE_SYNTHETIC_SOURCE"
        assert result["cleanup_failed"] == [role]
    finally:
        if replacements:
            with admin.connect() as db:
                db.execute(text(f'DROP ROLE IF EXISTS "{role}"'))
        admin.dispose()
