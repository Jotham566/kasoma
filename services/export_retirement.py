"""One parameter-free SQL batch through a separately authenticated, least-privilege login."""

import logging
from typing import Any, Literal
from uuid import UUID

from pydantic import Field, model_validator
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import Engine, make_url

from services.export_retirement_config import ExecutorSettings, isolated_scope
from services.export_retirement_install import owner_name
from services.identity_contracts import Contract

TABLES = (
    "data_request_receipts",
    "data_request_reviews",
    "personal_export_jobs",
    "data_subject_requests",
)
TASK_NAME = "kasoma.retire_export_evidence"
QUEUE = "privacy-maintenance"


class Removed(Contract):
    data_request_receipts: int = Field(default=0, ge=0, le=100)
    data_request_reviews: int = Field(default=0, ge=0, le=100)
    personal_export_jobs: int = Field(default=0, ge=0, le=100)
    data_subject_requests: int = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def total(self) -> "Removed":
        if sum(self.model_dump().values()) > 100:
            raise ValueError("Invalid retirement removal bound")
        return self


class Skipped(Contract):
    HELD: int = Field(default=0, ge=0, le=200)
    INELIGIBLE: int = Field(default=0, ge=0, le=200)
    DEPENDENCY: int = Field(default=0, ge=0, le=200)
    BUSY: int = Field(default=0, ge=0, le=200)


class Batch(Contract):
    status: Literal["PROCESSED", "DISABLED", "BUSY"]
    batch_id: UUID | None = None
    examined: int = Field(default=0, ge=0, le=200)
    removed: Removed = Field(default_factory=Removed)
    skipped: Skipped = Field(default_factory=Skipped)
    exhausted: bool = False

    @model_validator(mode="after")
    def conservation(self) -> "Batch":
        removed = sum(self.removed.model_dump().values())
        skipped = sum(self.skipped.model_dump().values())
        if self.status == "PROCESSED":
            if self.batch_id is None or removed + skipped != self.examined:
                raise ValueError("Invalid retirement batch accounting")
        elif self.batch_id is not None or self.examined or removed or skipped or self.exhausted:
            raise ValueError("Invalid inactive retirement batch")
        return self


class RetirementUnavailable(Exception):
    pass


def executor_engine(settings: ExecutorSettings) -> Engine:
    if settings.database_url is None:
        raise RetirementUnavailable("RETIREMENT_CONFIGURATION_UNAVAILABLE")
    url = make_url(settings.database_url.get_secret_value())
    options = url.query.get("options", "")
    return create_engine(
        url,
        hide_parameters=True,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 2,
            "options": f"{options} -c timezone=UTC -c statement_timeout=2000",
        },
    )


def profile(db: Connection) -> tuple[str, str]:
    """Metadata only: no source rows, credentials or arbitrary SQL/target arguments."""
    (
        database,
        schema,
        user,
        session,
        login,
        superuser,
        create_db,
        create_role,
        inherit,
        replicate,
        bypass,
    ) = db.execute(
        text("""
      SELECT current_database(),current_schema(),current_user,session_user,
        rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolinherit,rolreplication,rolbypassrls
      FROM pg_catalog.pg_roles WHERE rolname=current_user
    """)
    ).one()
    if (
        not isolated_scope(database, schema)
        or user != session
        or not login
        or any([superuser, create_db, create_role, inherit, replicate, bypass])
    ):
        raise RetirementUnavailable("RETIREMENT_ROLE_OR_SCOPE_REFUSED")
    owner = owner_name(database, schema)
    safe = db.scalar(
        text("""
      WITH scoped_tables AS MATERIALIZED (
        SELECT oid FROM pg_catalog.pg_class WHERE relnamespace=(
          SELECT oid FROM pg_catalog.pg_namespace WHERE nspname=:schema)
          AND relkind IN ('r','p'))
      SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_proc p
        JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
        JOIN pg_catalog.pg_roles r ON r.oid=p.proowner
        WHERE n.nspname=:schema AND p.proname='retire_completed_export_evidence'
          AND p.pronargs=0 AND p.prosecdef AND r.rolname=:owner
          AND NOT (r.rolcanlogin OR r.rolsuper OR r.rolcreatedb OR r.rolcreaterole
            OR r.rolinherit OR r.rolreplication OR r.rolbypassrls)
          AND has_function_privilege(current_user,p.oid,'EXECUTE')
          AND EXISTS(SELECT 1 FROM unnest(p.proconfig) setting
            WHERE replace(setting,' ','')=
              'search_path=pg_catalog,'||quote_ident(:schema)||',pg_temp')
          AND EXISTS(SELECT 1 FROM unnest(p.proconfig) setting WHERE lower(setting)='timezone=utc')
          AND EXISTS(SELECT 1 FROM unnest(p.proconfig) setting
            WHERE setting IN ('statement_timeout=2000ms','statement_timeout=2s',
              'statement_timeout=2000'))
          AND EXISTS(SELECT 1 FROM unnest(p.proconfig) setting
            WHERE setting IN ('lock_timeout=100ms','lock_timeout=100'))
          AND NOT EXISTS(SELECT 1 FROM aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a
            WHERE a.grantee=0 AND a.privilege_type='EXECUTE'))
        AND NOT has_schema_privilege(current_user,:schema,'CREATE')
        AND NOT has_database_privilege(current_user,current_database(),'CREATE')
        AND NOT EXISTS(SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member
          WHERE r.rolname=current_user)
        AND NOT EXISTS(SELECT 1 FROM scoped_tables c
          WHERE (has_table_privilege(current_user,c.oid,'SELECT')
            OR has_table_privilege(current_user,c.oid,'INSERT')
            OR has_table_privilege(current_user,c.oid,'UPDATE')
            OR has_table_privilege(current_user,c.oid,'DELETE')
            OR has_any_column_privilege(current_user,c.oid,'SELECT')
            OR has_any_column_privilege(current_user,c.oid,'UPDATE')
            OR has_any_column_privilege(current_user,c.oid,'INSERT')))
    """),
        {"schema": schema, "owner": owner},
    )
    if safe is not True:
        raise RetirementUnavailable("RETIREMENT_ROLE_OR_SCOPE_REFUSED")
    return database, schema


def execute(settings: ExecutorSettings) -> tuple[Batch, tuple[str, str] | None]:
    if not settings.enabled:
        return Batch(status="DISABLED"), None
    engine = None
    try:
        engine = executor_engine(settings)
        with engine.begin() as db:
            scope = profile(db)
            expected_database = (
                make_url(settings.database_url.get_secret_value()).database
                if settings.database_url
                else None
            )
            if scope != (expected_database, settings.namespace):
                raise RetirementUnavailable("RETIREMENT_ROLE_OR_SCOPE_REFUSED")
            qualified = db.dialect.identifier_preparer.quote_schema(scope[1])
            raw: Any = db.scalar(text(f"SELECT {qualified}.retire_completed_export_evidence()"))
            result = Batch.model_validate(raw)
        return result, scope
    except Exception:
        # Connection/SQL/validation failures may contain credentials or source context.
        raise RetirementUnavailable("RETIREMENT_EXECUTION_UNAVAILABLE") from None
    finally:
        if engine is not None:
            try:
                engine.dispose()
            except Exception:
                # Preserve the confirmed transaction outcome; withhold connection diagnostics.
                logging.getLogger("kasoma").warning("Retirement connection cleanup unavailable")
