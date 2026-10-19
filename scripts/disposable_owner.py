"""Exact owned-role lifecycle for generated local verification databases only."""

import re

from sqlalchemy import Engine, text

from services.export_retirement_install import owner_name


def validate_owner_database(name: str) -> str:
    if not re.fullmatch(r"kasoma_(?:load|drill_src)_[0-9a-f]{32}", name):
        raise ValueError("Only generated verification source databases are allowed")
    return name


def create_owner(admin: Engine, name: str) -> int:
    """Exclusively create the fresh owner and confirm its identity before commit."""
    role = owner_name(validate_owner_database(name), "public")
    with admin.connect().execution_options(isolation_level="READ COMMITTED") as db:
        with db.begin():
            db.execute(
                text(
                    f'CREATE ROLE "{role}" NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE '
                    "NOINHERIT NOREPLICATION NOBYPASSRLS"
                )
            )
            oid = db.scalar(
                text("SELECT oid FROM pg_catalog.pg_roles WHERE rolname=:role"), {"role": role}
            )
            if not isinstance(oid, int) or isinstance(oid, bool) or oid <= 0:
                raise RuntimeError("Isolated owner identity unavailable")
    return oid


def cleanup_owner(admin: Engine, name: str, owner_oid: int) -> None:
    """Inspect only the owner derived from this invocation's dropped database."""
    role = owner_name(validate_owner_database(name), "public")
    with admin.connect() as db:
        safe = db.scalar(
            text("""
              SELECT r.oid=:owner_oid AND NOT (
                r.rolcanlogin OR r.rolsuper OR r.rolcreatedb OR r.rolcreaterole
                OR r.rolinherit OR r.rolreplication OR r.rolbypassrls OR EXISTS(
                  SELECT 1 FROM pg_catalog.pg_auth_members m
                  WHERE m.roleid=r.oid OR m.member=r.oid))
              FROM pg_catalog.pg_roles r WHERE r.rolname=:role
            """),
            {"role": role, "owner_oid": owner_oid},
        )
        if safe is None:
            return
        if safe is not True:
            raise RuntimeError("Isolated owner cleanup refused")
        # Restrictive DROP preserves PostgreSQL's cross-database dependency checks.
        db.execute(text(f'DROP ROLE "{role}"'))
