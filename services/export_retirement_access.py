"""Privileged, synthetic-only provisioning; never imported by the execution worker."""

import os
import secrets
from pathlib import Path

from psycopg import sql
from sqlalchemy import Connection, text
from sqlalchemy.engine import make_url

from services.export_retirement_config import isolated_scope
from services.export_retirement_install import owner_name


def provision(db: Connection, path: Path, database_url: str, redis_url: str) -> None:
    """Create one isolated LOGIN and exclusive0600 configuration; never change existing roles."""
    database, schema, authorized = db.execute(
        text("""
      SELECT current_database(),current_schema(),
        pg_has_role(current_user,n.nspowner,'USAGE') AND
        (r.rolsuper OR r.rolcreaterole)
      FROM pg_namespace n JOIN pg_roles r ON r.rolname=current_user
      WHERE n.nspname=current_schema()
    """)
    ).one()
    if not authorized or not isolated_scope(database, schema):
        raise ValueError("Retirement provisioning requires an owned isolated synthetic scope")
    installed_owner = db.scalar(
        text("""
      SELECT r.rolname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
        JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname=:schema
        AND p.proname='retire_completed_export_evidence' AND p.pronargs=0 AND p.prosecdef
    """),
        {"schema": schema},
    )
    if installed_owner != owner_name(database, schema):
        raise ValueError("Retirement migration/ownership required")
    role = installed_owner.replace("kasoma_er_", "kasoma_ex_", 1)
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:role,0))"), {"role": role})
    if db.scalar(text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=:role)"), {"role": role}):
        raise ValueError("Existing retirement executor requires explicit rotation or recovery")
    if path.exists() or path.is_symlink():
        raise ValueError("Existing executor configuration is preserved")
    password = secrets.token_urlsafe(32)
    db.execute(
        text("SELECT set_config('kasoma.retirement_password',:password,true)"),
        {"password": password},
    )
    statement = sql.SQL("""
      DO $$ BEGIN
        EXECUTE format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
          NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD %L', {role_value},
          current_setting('kasoma.retirement_password'));
      END $$;
      GRANT USAGE ON SCHEMA {schema} TO {role};
      GRANT EXECUTE ON FUNCTION {schema}.retire_completed_export_evidence() TO {role};
      ALTER ROLE {role} SET search_path={schema},pg_catalog;
      ALTER ROLE {role} SET timezone='UTC';
      ALTER ROLE {role} SET statement_timeout='2000ms';
      ALTER ROLE {role} SET lock_timeout='100ms';
    """).format(
        role=sql.Identifier(role), role_value=sql.Literal(role), schema=sql.Identifier(schema)
    )
    try:
        db.execute(text(statement.as_string()))
    except Exception:
        raise RuntimeError("Executor role provisioning failed; diagnostics withheld") from None
    url = make_url(database_url).set(username=role, password=password)
    # Remove inherited role/search-path options: the new role has its own pinned default.
    url = url.set(query={})
    values = {
        "EXPORT_RETIREMENT_ENABLED": "false",
        "EXPORT_RETIREMENT_HOLDS_ENABLED": "false",
        "EXPORT_RETIREMENT_NAMESPACE": schema,
        "EXPORT_RETIREMENT_DATABASE_URL": url.render_as_string(hide_password=False),
        "EXPORT_RETIREMENT_REDIS_URL": redis_url,
    }
    # repr quotes prevent whitespace, quotes and special password characters changing dotenv syntax.
    payload = "".join(f"{key}={value!r}\n" for key, value in values.items())
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)  # Only this operation's exclusively created file.
        raise RuntimeError("Executor configuration write failed; diagnostics withheld") from None
