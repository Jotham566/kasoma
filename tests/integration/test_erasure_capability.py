"""ADR-071 actual-login disabled bootstrap, no account closure or erasure."""

import os
import subprocess
from contextlib import contextmanager

import pytest
from psycopg import sql
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from scripts.browser_database import cleanup_on_termination, pinned_local_docker
from scripts.erasure_capability import CapabilityInstallUnavailable, install
from scripts.erasure_scope import fresh_erasure_scope
from scripts.recovery_containers import command
from services.database import engine_for
from tests.integration.test_erasure_scope import synthetic_profile

pytestmark = pytest.mark.integration


@contextmanager
def source():
    with cleanup_on_termination(), fresh_erasure_scope(synthetic_profile()) as proof:
        subprocess.run(
            ["make", "migrate"],
            capture_output=True,
            check=True,
            timeout=90,
            env=os.environ | {"DATABASE_URL": proof.settings.database_url.get_secret_value()},
        )
        yield proof
    with pinned_local_docker():
        assert (
            proof._container_id
            not in command(
                ["docker", "ps", "--all", "--no-trunc", "--format", "{{.ID}}"]
            ).splitlines()
        )


def denied(engine, query):
    with pytest.raises(DBAPIError) as error, engine.begin() as db:
        db.execute(text(query))
    assert error.value.orig.sqlstate == "42501"


def test_actual_logins_have_only_disabled_readiness_and_no_owner_or_source_rights():
    with source() as proof:
        capability = install(proof)
        namespace = sql.Identifier(capability.namespace).as_string()
        admin = engine_for(proof.settings)
        try:
            with admin.connect() as db:
                inventory = db.execute(
                    text("""
                  SELECT count(*),sum((SELECT count(*) FROM pg_catalog.pg_attribute a
                    WHERE a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped))
                  FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n
                    ON n.oid=c.relnamespace
                  WHERE c.relkind='r' AND n.nspname IN ('public',:namespace)
                """),
                    {"namespace": capability.namespace},
                ).one()
                assert tuple(inventory) == (75, 561)
        finally:
            admin.dispose()
        for url in [capability.authorizer_url, capability.executor_url]:
            engine = engine_for(proof.settings.model_copy(update={"database_url": url}))
            try:
                with engine.connect() as db:
                    principal = db.execute(
                        text(
                            "SELECT oid,rolsuper,rolcreatedb,rolcreaterole,rolinherit,"
                            "rolreplication,rolbypassrls FROM pg_catalog.pg_roles "
                            "WHERE rolname=current_user"
                        )
                    ).one()
                    assert principal[0] in [capability.authorizer_oid, capability.executor_oid]
                    assert tuple(principal[1:]) == (False,) * 6
                    assert db.scalar(text(f"SELECT {namespace}.readiness()")) == {
                        "version": "isolated-erasure-capability-v3",
                        "creation_enabled": False,
                        "execution_enabled": False,
                    }
                    owner = db.scalar(
                        text("SELECT rolname FROM pg_catalog.pg_roles WHERE oid=:owner"),
                        {"owner": capability.owner_oid},
                    )
                for query in [
                    "SELECT * FROM public.users",
                    f"SELECT * FROM {namespace}.control",
                    f"SELECT {namespace}.scope_identity_ok()",
                    f"SELECT {namespace}.initialize_control(NULL)",
                    "UPDATE public.users SET closed_at=clock_timestamp()",
                    "INSERT INTO public.account_erasure_jobs DEFAULT VALUES",
                    "DELETE FROM public.attempts",
                    f"SET ROLE {sql.Identifier(owner).as_string()}",
                ]:
                    denied(engine, query)
                with engine.begin() as db:
                    db.execute(
                        text("CREATE TEMP TABLE account_erasure_state(creation_enabled boolean)")
                    )
                    db.execute(text("SET LOCAL search_path=pg_temp,public"))
                    assert not db.scalar(text(f"SELECT {namespace}.readiness()"))[
                        "execution_enabled"
                    ]
            finally:
                engine.dispose()
        with pytest.raises(CapabilityInstallUnavailable):
            install(proof)


def test_existing_role_is_never_adopted_and_failed_install_is_atomic():
    with source() as proof:
        admin = engine_for(proof.settings)
        owner = "kasoma_eo_" + proof.nonce.hex
        try:
            with admin.begin() as db:
                db.execute(
                    text(
                        sql.SQL("CREATE ROLE {} NOLOGIN").format(sql.Identifier(owner)).as_string()
                    )
                )
                before = db.scalar(
                    text("SELECT oid FROM pg_catalog.pg_roles WHERE rolname=:role"), {"role": owner}
                )
            with pytest.raises(CapabilityInstallUnavailable):
                install(proof)
            with admin.connect() as db:
                assert (
                    db.scalar(
                        text("SELECT oid FROM pg_catalog.pg_roles WHERE rolname=:role"),
                        {"role": owner},
                    )
                    == before
                )
                assert (
                    db.scalar(
                        text("SELECT to_regnamespace(:namespace)"),
                        {"namespace": "kasoma_cap_" + proof.nonce.hex},
                    )
                    is None
                )
                state = db.execute(
                    text(
                        "SELECT original_scope_eligible,creation_enabled,execution_enabled,"
                        "owner_oid,executor_oid FROM public.account_erasure_state"
                    )
                ).one()
                assert tuple(state) == (False, False, False, None, None)
        finally:
            admin.dispose()


def test_private_hmac_matches_standard_and_failed_key_insert_is_redacted_and_atomic(monkeypatch):
    import hmac
    import secrets
    from types import SimpleNamespace
    from uuid import uuid4

    from scripts import erasure_capability as bootstrap

    with source() as proof:
        marker = b"synthetic-rejected-key-" + uuid4().hex.encode()
        original = bootstrap.secrets
        passwords = []

        def password(length):
            value = secrets.token_urlsafe(length)
            passwords.append(value)
            return value

        monkeypatch.setattr(
            bootstrap,
            "secrets",
            SimpleNamespace(
                token_urlsafe=password,
                token_bytes=lambda length: marker,
            ),
        )
        with pytest.raises(CapabilityInstallUnavailable) as error:
            install(proof)
        assert error.value.phase == "CONTROL"
        admin = engine_for(proof.settings)
        try:
            with admin.connect() as db:
                assert (
                    db.scalar(
                        text("SELECT to_regnamespace(:name)"),
                        {
                            "name": "kasoma_cap_" + proof.nonce.hex,
                        },
                    )
                    is None
                )
                assert not db.scalar(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_roles WHERE rolname=ANY(:names))"
                    ),
                    {
                        "names": [
                            prefix + proof.nonce.hex
                            for prefix in ["kasoma_eo_", "kasoma_ea_", "kasoma_ex_"]
                        ]
                    },
                )
                assert not db.scalar(
                    text("SELECT original_scope_eligible FROM public.account_erasure_state")
                )
            try:
                captured = subprocess.run(
                    ["docker", "logs", "--tail", "400", proof._container_id],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                raise RuntimeError("Owned synthetic log probe unavailable") from None
            logs = captured.stdout + captured.stderr
            # Never let assertion rendering print raw logs or any credential.
            leaked = any(value in logs for value in [marker.decode(), marker.hex(), *passwords])
            password_count = len(passwords)
            observed = "Erasure control initialization unavailable" in logs
            assert password_count == 2 and leaked is False and observed is True
            monkeypatch.setattr(bootstrap, "secrets", original)
            capability = install(proof)
            owner = sql.Identifier("kasoma_eo_" + proof.nonce.hex).as_string()
            crypto = sql.Identifier("kasoma_ec_" + proof.nonce.hex).as_string()
            with admin.begin() as db:
                db.execute(text("SET LOCAL ROLE " + owner))
                value = db.scalar(
                    text("SELECT " + crypto + ".hmac(:message,:key,'sha256')"),
                    {
                        "message": b"Hi There",
                        "key": b"\x0b" * 20,
                    },
                )
                assert bytes(value) == hmac.digest(b"\x0b" * 20, b"Hi There", "sha256")
            denied(admin, "UPDATE public.account_erasure_state SET creation_enabled=true")
            # Readiness contains neither private key, source data nor role identities.
            assert capability.owner_oid > 0
        finally:
            admin.dispose()


def test_unknown_private_namespace_prevents_installation():
    with source() as proof:
        admin = engine_for(proof.settings)
        try:
            with admin.begin() as db:
                db.execute(text("CREATE SCHEMA synthetic_unknown_private_source"))
            with pytest.raises(CapabilityInstallUnavailable):
                install(proof)
        finally:
            admin.dispose()


def test_installed_readiness_rechecks_role_flags_and_crypto_namespace_identity():
    with source() as proof:
        capability = install(proof)
        owner = sql.Identifier("kasoma_eo_" + proof.nonce.hex).as_string()
        crypto_name = "kasoma_ec_" + proof.nonce.hex
        crypto = sql.Identifier(crypto_name).as_string()
        renamed = sql.Identifier("synthetic_renamed_crypto").as_string()
        namespace = sql.Identifier(capability.namespace).as_string()
        admin = engine_for(proof.settings)
        executor = engine_for(
            proof.settings.model_copy(
                update={"database_url": capability.executor_url},
            )
        )
        try:
            with admin.begin() as db:
                db.execute(text("ALTER ROLE " + owner + " LOGIN"))
            denied(executor, "SELECT " + namespace + ".readiness()")
            with admin.begin() as db:
                db.execute(text("ALTER ROLE " + owner + " NOLOGIN"))
                db.execute(text("ALTER SCHEMA " + crypto + " RENAME TO " + renamed))
            denied(executor, "SELECT " + namespace + ".readiness()")
            with admin.begin() as db:
                db.execute(text("ALTER SCHEMA " + renamed + " RENAME TO " + crypto))
            with executor.connect() as db:
                assert not db.scalar(text("SELECT " + namespace + ".readiness()"))[
                    "execution_enabled"
                ]
        finally:
            executor.dispose()
            admin.dispose()
