"""ADR-073 pre-install catalog fence; not installed SQL or erasure clearance."""

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Self

from psycopg import sql
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError

ROOT = Path(__file__).resolve().parents[1]
CATALOG_SQL = ROOT / "services/erasure_catalog.sql"
RAW_SQL = ROOT / "services/erasure_catalog_raw.sql"
RAW_CATEGORIES = frozenset(
    {
        "functions",
        "types",
        "defaults",
        "constraints",
        "indexes",
        "triggers",
        "policies",
        "rules",
        "relations",
    }
)
BASELINE_PATH = ROOT / "services/erasure_catalog_v1.json"
DYNAMIC_BODIES = MappingProxyType(
    {
        "export_retirement_owner_safe": "body_owner",
        "export_retirement_leaf_guard": "body_leaf",
        "personal_export_job_guard": "body_job",
        "data_request_completion_guard": "body_request",
    }
)
OWNER_PLACEHOLDER = "@EXPORT_RETIREMENT_OWNER@"
CATEGORIES = frozenset(
    "roles memberships database database_settings namespace relations attributes constraints "
    "indexes "
    "triggers functions aggregates types enums acl attribute_acl default_acl policies rules "
    "extensions operators "
    "casts opclasses opfamilies amop amproc inheritance collations conversions event_triggers "
    "foreign_controls text_search".split()
)


class CatalogUnavailable(ValueError):
    def __init__(self, code: str = "MISMATCH", position: int = 0) -> None:
        # Only a closed SQLSTATE vocabulary and numeric static-query position escape.
        self.code = (
            code if code in {"MISMATCH", "42703", "42883", "42601", "42501", "XX000"} else "QUERY"
        )
        self.position = max(0, min(position, 100000))
        super().__init__("ERASURE_CATALOG_UNAVAILABLE")


class CatalogDigest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    count: int = Field(ge=0)
    digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class CatalogBaseline(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    profile: Literal["public-preinstall-catalog-v1"] = "public-preinstall-catalog-v1"
    revision: Literal["0045"] = "0045"
    postgres_major: Literal[16] = 16
    migration_sources_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    raw_categories: dict[str, CatalogDigest]
    categories: dict[str, CatalogDigest]
    body_templates: dict[str, str]

    @model_validator(mode="after")
    def closed_categories(self) -> Self:
        if self.body_templates.keys() != DYNAMIC_BODIES.keys():
            raise ValueError("Unsupported body templates")
        if any(OWNER_PLACEHOLDER not in body for body in self.body_templates.values()):
            raise ValueError("Missing exact owner placeholder")
        if self.raw_categories.keys() != RAW_CATEGORIES:
            raise ValueError("Unsupported raw safety categories")
        if self.categories.keys() != CATEGORIES:
            raise ValueError("Unsupported catalog categories")
        return self


def migration_digest() -> str:
    """Bind the reproducible artifact to the ordinary versioned migration recipe."""
    folder = ROOT / "apps/api/migrations"
    paths = [folder / "env.py", ROOT / "services/export_retirement_install.py"]
    paths += sorted((folder / "versions").glob("[0-9][0-9][0-9][0-9]_*.py"))
    paths += sorted((folder / "sql").glob("[0-9][0-9][0-9][0-9]_*.sql"))
    digest = hashlib.sha256()
    for path in paths:
        name = str(path.relative_to(ROOT)).encode()
        body = path.read_bytes()
        digest.update(len(name).to_bytes(4, "big") + name)
        digest.update(len(body).to_bytes(8, "big") + body)
    return digest.hexdigest()


def retirement_owner(database: str) -> str:
    # Exact frozen ADR-060 derivation, not a role-prefix matcher or caller override.
    return "kasoma_er_" + hashlib.sha256(f"{database}:public".encode()).hexdigest()[:24]


def catalog_queries() -> tuple[str, str]:
    """Compile only closed repository SQL and expected-template parameter names."""
    choices = [
        sql.SQL(
            "WHEN p.proname={} THEN CASE WHEN p.prosrc={} "
            "THEN 'APPROVED_EXPORT_BODY' ELSE 'UNSUPPORTED_EXPORT_BODY' END"
        ).format(sql.Literal(name), sql.SQL(":" + parameter))
        for name, parameter in DYNAMIC_BODIES.items()
    ]
    expression = (
        sql.SQL("CASE ") + sql.SQL(" ").join(choices) + sql.SQL(" ELSE p.prosrc END")
    ).as_string()
    full = CATALOG_SQL.read_text()
    raw = RAW_SQL.read_text()
    if full.count("__DYNAMIC_BODY__") != 1 or raw.count("__DYNAMIC_BODY__") != 1:
        raise CatalogUnavailable()
    prefix = full.split(", acl_objects AS (", 1)
    if len(prefix) != 2:
        raise CatalogUnavailable()
    return (
        full.replace("__DYNAMIC_BODY__", expression),
        (prefix[0] + raw).replace("__DYNAMIC_BODY__", expression),
    )


def _observe_catalog(
    db: Connection,
    templates: dict[str, str],
    *,
    raw_expected: dict[str, CatalogDigest] | None,
) -> CatalogBaseline:
    """Caller owns transaction. Only fresh generation may omit the raw expected fence."""
    try:
        if not db.in_transaction():
            raise CatalogUnavailable()
        # Roll back local settings and any aborted catalog query on all failure paths.
        with db.begin_nested():
            return _snapshot(db, templates, raw_expected=raw_expected)
    except CatalogUnavailable:
        raise
    except DBAPIError as failure:
        diag = getattr(failure.orig, "diag", None)
        position = getattr(diag, "statement_position", "0") or "0"
        raise CatalogUnavailable(
            getattr(failure.orig, "sqlstate", "QUERY"),
            int(position) if str(position).isdigit() else 0,
        ) from None
    except Exception:
        raise CatalogUnavailable() from None


def _snapshot(
    db: Connection,
    templates: dict[str, str],
    *,
    raw_expected: dict[str, CatalogDigest] | None,
) -> CatalogBaseline:
    if (
        not db.in_transaction()
        or db.scalar(text("SELECT current_schema()")) != "public"
        or int(str(db.scalar(text("SHOW server_version_num")))) // 10000 != 16
    ):
        raise CatalogUnavailable()
    previous_path = db.scalar(text("SHOW search_path"))
    previous_zone = db.scalar(text("SHOW timezone"))
    previous_statement = db.scalar(text("SHOW statement_timeout"))
    previous_lock = db.scalar(text("SHOW lock_timeout"))
    db.execute(text("SET LOCAL statement_timeout='5000ms'"))
    db.execute(text("SET LOCAL lock_timeout='100ms'"))
    db.execute(text("SET LOCAL search_path=pg_catalog"))
    db.execute(text("SET LOCAL timezone='UTC'"))
    if templates.keys() != DYNAMIC_BODIES.keys():
        raise CatalogUnavailable()
    database = db.scalar(text("SELECT current_database()"))
    if not isinstance(database, str):
        raise CatalogUnavailable()
    owner = retirement_owner(database)
    parameters = {"retirement_owner": owner} | {
        parameter: templates[name].replace(OWNER_PLACEHOLDER, owner)
        for name, parameter in DYNAMIC_BODIES.items()
    }
    full_query, raw_query = catalog_queries()
    raw_rows = db.execute(text(raw_query), parameters).mappings().all()
    raw = {
        row["category"]: CatalogDigest(count=row["count"], digest=row["digest"]) for row in raw_rows
    }
    if raw.keys() != RAW_CATEGORIES or (raw_expected is not None and raw != raw_expected):
        raise CatalogUnavailable()
    rows = db.execute(text(full_query), parameters).mappings().all()
    result = CatalogBaseline(
        migration_sources_sha256=migration_digest(),
        body_templates=templates,
        raw_categories=raw,
        categories={
            row["category"]: CatalogDigest(count=row["count"], digest=row["digest"]) for row in rows
        },
    )
    db.execute(text("SELECT set_config('search_path',:path,true)"), {"path": previous_path})
    db.execute(text("SELECT set_config('timezone',:zone,true)"), {"zone": previous_zone})
    db.execute(
        text("SELECT set_config('statement_timeout',:timeout,true)"),
        {"timeout": previous_statement},
    )
    db.execute(text("SELECT set_config('lock_timeout',:timeout,true)"), {"timeout": previous_lock})
    return result


def load_baseline() -> CatalogBaseline:
    try:
        baseline = CatalogBaseline.model_validate_json(BASELINE_PATH.read_bytes())
        if baseline.migration_sources_sha256 != migration_digest():
            raise CatalogUnavailable()
        return baseline
    except Exception:
        raise CatalogUnavailable() from None


def observe_catalog(db: Connection) -> CatalogBaseline:
    # Render only the checked versioned expected templates. Never normalize live bodies.
    baseline = load_baseline()
    return _observe_catalog(db, baseline.body_templates, raw_expected=baseline.raw_categories)


def check_preinstall_catalog(db: Connection) -> None:
    if observe_catalog(db) != load_baseline():
        raise CatalogUnavailable()


def baseline_text(baseline: CatalogBaseline) -> str:
    return json.dumps(baseline.model_dump(), indent=2, sort_keys=True) + "\n"
