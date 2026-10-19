"""Frozen ADR-060 SQL installer; privileged migration tooling, never an API capability."""

import hashlib
import re
from pathlib import Path

from psycopg import sql
from sqlalchemy import Connection, text

SQL_SOURCE = Path(__file__).parents[1] / "apps/api/migrations/sql/0041_export_retirement.sql"


def owner_name(database: str, schema: str) -> str:
    return "kasoma_er_" + hashlib.sha256(f"{database}:{schema}".encode()).hexdigest()[:24]


def install_v1(connection: Connection) -> str:
    """Derive a database/schema-specific NOLOGIN owner; grant no executor membership."""
    schema = connection.scalar(text("SELECT current_schema()"))
    database = connection.scalar(text("SELECT current_database()"))
    if not isinstance(schema, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,62}", schema):
        raise ValueError("Unsupported migration schema")
    if not isinstance(database, str):
        raise ValueError("Unsupported migration database")
    owner = owner_name(database, schema)
    quoted = connection.dialect.identifier_preparer.quote_schema(schema)
    # The role name is generated hex, never a caller-supplied SQL identifier.
    role_ddl = sql.SQL("""
      DO $$ BEGIN
        IF NOT EXISTS(SELECT 1 FROM pg_catalog.pg_roles WHERE rolname={owner_value}) THEN
          CREATE ROLE {owner} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
            NOINHERIT NOREPLICATION NOBYPASSRLS;
        END IF;
        IF EXISTS(SELECT 1 FROM pg_catalog.pg_roles WHERE rolname={owner_value}
          AND (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit
            OR rolreplication OR rolbypassrls)) OR EXISTS(
          SELECT 1 FROM pg_catalog.pg_auth_members m JOIN pg_catalog.pg_roles r ON r.oid=m.member
          WHERE r.rolname={owner_value})
        THEN RAISE EXCEPTION 'Unsafe retirement owner role'; END IF;
      END $$;
    """).format(owner=sql.Identifier(owner), owner_value=sql.Literal(owner))
    connection.exec_driver_sql(role_ddl.as_string())
    ddl = SQL_SOURCE.read_text().replace("__SCHEMA__", quoted).replace("__OWNER__", owner)
    ddl = ddl.replace("__SCHEMA_NAME__", schema)
    connection.execute(text(ddl))
    return owner
