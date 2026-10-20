"""ADR-061 fresh bootstrap provenance only; never executes closure or erasure."""

import os
import subprocess
from dataclasses import FrozenInstanceError, replace

import pytest
from sqlalchemy import text

from scripts.browser_database import cleanup_on_termination, pinned_local_docker
from scripts.erasure_scope import FreshScopeUnavailable, fresh_erasure_scope
from scripts.recovery_containers import command
from services.config import Settings
from services.database import engine_for

pytestmark = pytest.mark.integration


def synthetic_profile():
    # The root connection is checked as local configuration but never opened.
    return Settings(
        model_provider="fake",
        email_provider="fake",
        sms_provider="fake",
        whatsapp_provider="fake",
        allow_external_api_calls=False,
    )


def test_fresh_source_survives_migrations_but_cannot_be_reconstructed_or_retargeted():
    with cleanup_on_termination(), fresh_erasure_scope(synthetic_profile()) as proof:
        proof.verify()
        assert proof.database_oid > 0 and proof.namespace_oid > 0
        with pytest.raises(FrozenInstanceError):
            proof.database_oid = 1
        # Even a clone with identical fields/issuer is not a factory-issued object.
        with pytest.raises(FreshScopeUnavailable):
            replace(proof).verify()
        assert "postgresql" not in repr(proof)
        assert proof.settings.database_url.get_secret_value() not in repr(proof)
        for _ in range(2):
            subprocess.run(
                ["make", "migrate"],
                env=os.environ | {"DATABASE_URL": proof.settings.database_url.get_secret_value()},
                capture_output=True,
                check=True,
                timeout=90,
            )
        proof.verify()
        engine = engine_for(proof.settings)
        try:
            with engine.connect() as db:
                assert db.scalar(text("SELECT version_num FROM alembic_version")) == "0045"
                assert db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) == 0
                assert db.scalar(text("SELECT count(*) FROM users")) == 0
                flags = db.execute(
                    text(
                        "SELECT original_scope_eligible,creation_enabled,execution_enabled "
                        "FROM account_erasure_state"
                    )
                ).one()
                assert tuple(flags) == (False, False, False)
        finally:
            engine.dispose()
    with pytest.raises(FreshScopeUnavailable):
        proof.verify()
    with pinned_local_docker():
        assert (
            proof._container_id
            not in command(
                ["docker", "ps", "--all", "--no-trunc", "--format", "{{.ID}}"]
            ).splitlines()
        )


def test_already_populated_source_is_refused_even_during_factory_issuance(monkeypatch):
    from scripts import erasure_scope as scope

    original = scope._issue
    rejected = []
    containers = []

    def inject_existing_relation(ticket, owned, settings):
        containers.append(owned.created["source-db"])
        engine = engine_for(settings)
        try:
            with engine.begin() as db:
                db.execute(
                    text("CREATE TABLE public.synthetic_existing_source(id integer PRIMARY KEY)")
                )
        finally:
            engine.dispose()
        try:
            return original(ticket, owned, settings)
        except FreshScopeUnavailable:
            rejected.append(True)
            raise

    monkeypatch.setattr(scope, "_issue", inject_existing_relation)
    with cleanup_on_termination(), pytest.raises(RuntimeError, match="diagnostics withheld"):
        with fresh_erasure_scope(synthetic_profile()):
            pytest.fail("Already-populated source was adopted")
    assert rejected == [True] and len(containers) == 1
    with pinned_local_docker():
        assert (
            containers[0]
            not in command(
                ["docker", "ps", "--all", "--no-trunc", "--format", "{{.ID}}"]
            ).splitlines()
        )
