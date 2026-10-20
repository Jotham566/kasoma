"""ADR-061/071 privileged fresh-source SQL installer; never an API/worker import."""

import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from psycopg import sql
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url

from scripts.erasure_scope import FreshErasureScope
from services.database import engine_for
from services.erasure_capability_contract import CAPABILITY_VERSION, CRYPTO_VERSION
from services.erasure_inventory import check_source_shape

SQL_SOURCE = Path(__file__).parents[1] / "apps/api/migrations/sql/erasure_capability_v1.sql"


InstallPhase = Literal["SOURCE", "ROLES", "LOGINS", "CRYPTO", "DEFINITION", "CONTROL", "HANDOFF"]


class CapabilityInstallUnavailable(RuntimeError):
    def __init__(self, phase: InstallPhase = "SOURCE") -> None:
        self.phase = phase
        super().__init__("ERASURE_CAPABILITY_INSTALL_UNAVAILABLE:" + phase)


@dataclass(frozen=True, repr=False)
class InstalledCapability:
    namespace: str
    owner_oid: int
    authorizer_oid: int
    executor_oid: int
    authorizer_url: SecretStr = field(repr=False)
    executor_url: SecretStr = field(repr=False)


def install(scope: FreshErasureScope) -> InstalledCapability:
    """Exclusively install disabled capability, never adopt roles or enable erasure."""
    scope.verify()
    suffix = scope.nonce.hex
    namespace, crypto = "kasoma_cap_" + suffix, "kasoma_ec_" + suffix
    owner, authorizer, executor = (
        "kasoma_eo_" + suffix,
        "kasoma_ea_" + suffix,
        "kasoma_ex_" + suffix,
    )
    passwords = {authorizer: secrets.token_urlsafe(32), executor: secrets.token_urlsafe(32)}
    engine = engine_for(scope.settings)
    phase: InstallPhase = "SOURCE"
    try:
        with engine.begin() as db:
            scope.verify()
            check_source_shape(db)
            if db.scalar(
                text("""
              SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_namespace
                WHERE nspname NOT IN ('public','pg_catalog','information_schema')
                  AND nspname NOT LIKE 'pg_toast%' AND nspname NOT LIKE 'pg_temp%')
            """)
            ):
                raise CapabilityInstallUnavailable()
            # A trusted fresh-source creator remains required, not a name-only test.
            actual = db.execute(
                text("""
              SELECT d.oid,n.oid,r.rolsuper FROM pg_catalog.pg_database d
              CROSS JOIN pg_catalog.pg_namespace n JOIN pg_catalog.pg_roles r
              ON r.rolname=current_user WHERE d.datname=current_database()
                AND n.nspname=current_schema()
            """)
            ).one()
            if tuple(actual) != (scope.database_oid, scope.namespace_oid, True):
                raise CapabilityInstallUnavailable()
            if not db.scalar(
                text("""
              SELECT pg_try_advisory_xact_lock(hashtextextended(
                'kasoma.erasure.bootstrap.v1:' || CAST(:database AS text) || ':' ||
                CAST(:namespace AS text),0) | (-9223372036854775808)::bigint)
            """),
                {"database": scope.database_oid, "namespace": scope.namespace_oid},
            ):
                raise CapabilityInstallUnavailable()
            if db.scalar(
                text("""
              SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_roles WHERE rolname=ANY(:roles))
                OR EXISTS(SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname=ANY(:schemas))
                OR EXISTS(SELECT 1 FROM pg_catalog.pg_extension WHERE extname='pgcrypto')
            """),
                {"roles": [owner, authorizer, executor], "schemas": [namespace, crypto]},
            ):
                raise CapabilityInstallUnavailable()
            phase = "ROLES"
            for role in [owner, authorizer, executor]:
                db.execute(
                    text(
                        sql.SQL(
                            "CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB "
                            "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS"
                        )
                        .format(sql.Identifier(role))
                        .as_string()
                    )
                )
            oids = dict(
                db.execute(
                    text("SELECT rolname,oid FROM pg_catalog.pg_roles WHERE rolname=ANY(:roles)"),
                    {"roles": [owner, authorizer, executor]},
                ).all()
            )
            phase = "LOGINS"
            for role, password in passwords.items():
                db.execute(
                    text("SELECT set_config('kasoma.bootstrap_password',:password,true)"),
                    {"password": password},
                )
                # Catch dynamic DDL failures inside SQL, before an expanded password
                # can become an uncaught statement/context in PostgreSQL error logs.
                statement = sql.SQL("""
                  DO $$ BEGIN
                    EXECUTE format('ALTER ROLE %I LOGIN PASSWORD %L',{},
                      current_setting('kasoma.bootstrap_password'));
                  EXCEPTION WHEN OTHERS THEN
                    RAISE EXCEPTION 'Erasure login initialization unavailable'
                      USING ERRCODE='P0001';
                  END $$;
                  ALTER ROLE {} SET search_path=pg_catalog;
                  ALTER ROLE {} SET timezone='UTC';
                  ALTER ROLE {} SET statement_timeout='2000ms';
                  ALTER ROLE {} SET lock_timeout='100ms';
                """).format(sql.Literal(role), *[sql.Identifier(role)] * 4)
                db.execute(text(statement.as_string()))
            phase = "CRYPTO"
            db.execute(
                text(
                    sql.SQL("CREATE SCHEMA {} AUTHORIZATION {}; CREATE SCHEMA {};")
                    .format(
                        sql.Identifier(namespace), sql.Identifier(owner), sql.Identifier(crypto)
                    )
                    .as_string()
                )
            )
            db.execute(
                text(
                    sql.SQL("CREATE EXTENSION pgcrypto WITH SCHEMA {}")
                    .format(sql.Identifier(crypto))
                    .as_string()
                )
            )
            version = db.scalar(
                text("SELECT extversion FROM pg_catalog.pg_extension WHERE extname='pgcrypto'")
            )
            if version != CRYPTO_VERSION:
                raise CapabilityInstallUnavailable()
            replacements = {
                "__CAP__": sql.Identifier(namespace).as_string(),
                "__CRYPTO__": sql.Identifier(crypto).as_string(),
                "__OWNER__": sql.Identifier(owner).as_string(),
                "__AUTHORIZER__": sql.Identifier(authorizer).as_string(),
                "__EXECUTOR__": sql.Identifier(executor).as_string(),
                "__OWNER_OID__": str(oids[owner]),
                "__AUTHORIZER_OID__": str(oids[authorizer]),
                "__EXECUTOR_OID__": str(oids[executor]),
                "__DATABASE_OID__": str(scope.database_oid),
                "__NAMESPACE_OID__": str(scope.namespace_oid),
                "__INSTALLATION_NONCE__": str(scope.nonce),
            }
            phase = "DEFINITION"
            ddl = SQL_SOURCE.read_text()
            for marker, value in replacements.items():
                ddl = ddl.replace(marker, value)
            if "__" in ddl:
                raise CapabilityInstallUnavailable()
            db.execute(text(ddl))
            phase = "CONTROL"
            # The server-side initializer catches row-validation failures before a
            # private key can appear in PostgreSQL CHECK error details.
            db.execute(
                text(sql.SQL("SET LOCAL ROLE {};").format(sql.Identifier(owner)).as_string())
            )
            db.execute(
                text(
                    sql.SQL("SELECT {}.initialize_control(:key)")
                    .format(sql.Identifier(namespace))
                    .as_string()
                ),
                {"key": secrets.token_bytes(32)},
            )
            installed_version = db.scalar(
                text(
                    sql.SQL("SELECT version FROM {}.control")
                    .format(sql.Identifier(namespace))
                    .as_string()
                )
            )
            if installed_version != CAPABILITY_VERSION:
                raise CapabilityInstallUnavailable()
            phase = "HANDOFF"
            db.execute(
                text(
                    "UPDATE public.account_erasure_state SET original_scope_eligible=true,"
                    "owner_oid=:owner,executor_oid=:executor"
                ),
                {"owner": oids[owner], "executor": oids[executor]},
            )
            scope.verify()
        url = make_url(scope.settings.database_url.get_secret_value())
        return InstalledCapability(
            namespace,
            oids[owner],
            oids[authorizer],
            oids[executor],
            SecretStr(
                url.set(username=authorizer, password=passwords[authorizer]).render_as_string(
                    hide_password=False
                )
            ),
            SecretStr(
                url.set(username=executor, password=passwords[executor]).render_as_string(
                    hide_password=False
                )
            ),
        )
    except Exception:
        raise CapabilityInstallUnavailable(phase) from None
    finally:
        engine.dispose()
