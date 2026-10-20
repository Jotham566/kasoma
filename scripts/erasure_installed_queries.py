"""ADR-079 closed installed metadata queries; no caller-selected SQL or fields."""

import re

from psycopg import sql
from sqlalchemy import Connection, text

from services.erasure_catalog import CATALOG_SQL, NODE_FIELDS, RAW_SQL
from services.erasure_catalog_bindings import BOUND_EXPRESSIONS, CatalogBindings
from services.erasure_datum import DATUM_PATTERN, datum_sql


def prepared_expressions(db: Connection, bindings: CatalogBindings) -> dict[str, str]:
    """Independent fresh generator only; the accepting verifier never reads templates."""
    constraint = (
        sql.SQL(
            "SELECT 'CONSTRAINT:'||CASE WHEN c.conrelid='public.account_erasure_state'::regclass "
            "THEN 'public.account_erasure_state' ELSE 'CAPABILITY.control' END||':'||c.conname "
            "AS key,{tree} AS tree "
            "FROM pg_catalog.pg_constraint c WHERE c.conrelid=to_regclass(:cap||'.control') "
            "OR (c.conrelid='public.account_erasure_state'::regclass "
            "AND c.conname='account_erasure_state_bound_owner')"
        )
        .format(tree=sql.SQL(datum_sql(sql.Identifier("c", "conbin"))))
        .as_string()
    )
    default = (
        sql.SQL(
            "SELECT 'DEFAULT:CAPABILITY.control:'||a.attname AS key,{tree} AS tree "
            "FROM pg_catalog.pg_attrdef d JOIN pg_catalog.pg_attribute a "
            "ON a.attrelid=d.adrelid AND a.attnum=d.adnum "
            "WHERE d.adrelid=to_regclass(:cap||'.control')"
        )
        .format(tree=sql.SQL(datum_sql(sql.Identifier("d", "adbin"))))
        .as_string()
    )
    parameters = {"cap": bindings.namespace, "datum_pattern": DATUM_PATTERN}
    rows = list(db.execute(text(constraint), parameters).mappings().all())
    rows.extend(db.execute(text(default), parameters).mappings().all())
    result = {str(row["key"]): str(row["tree"]) for row in rows if row["key"] in BOUND_EXPRESSIONS}
    if result.keys() != BOUND_EXPRESSIONS.keys():
        raise ValueError("Incomplete prepared expressions")
    return result


def _reference(value: str) -> str:
    # Only fixed catalog expressions below reach this compiler. This labels object
    # references, never arbitrary live code, expression text or payload values.
    return (
        "CASE WHEN starts_with("
        + value
        + ",:cap||'.') THEN 'CAPABILITY.'||substr("
        + value
        + ",length(:cap)+2) WHEN starts_with("
        + value
        + ",:crypto||'.') THEN 'CRYPTO.'||substr("
        + value
        + ",length(:crypto)+2) ELSE "
        + value
        + " END"
    )


def _namespace(oid: str, name: str) -> str:
    return (
        "CASE WHEN "
        + oid
        + "=to_regnamespace(:cap) THEN 'CAPABILITY' WHEN "
        + oid
        + "=to_regnamespace(:crypto) THEN 'CRYPTO' ELSE "
        + name
        + " END"
    )


def _body() -> str:
    return """CASE WHEN CAST(:code_hashes AS jsonb)?p.signature THEN
      CASE WHEN encode(sha256(convert_to(p.prosrc,'UTF8')),'hex')=
        (CAST(:code_hashes AS jsonb)->>p.signature)
        THEN 'APPROVED_RENDERED_BODY' ELSE 'UNSUPPORTED_RENDERED_BODY' END
      ELSE p.prosrc END"""


def _expression(key: str, value: str) -> str:
    return (
        "CASE WHEN CAST(:expression_hashes AS jsonb)?(" + key + ") THEN CASE WHEN "
        "encode(sha256(convert_to(" + value + ",'UTF8')),'hex')="
        "(CAST(:expression_hashes AS jsonb)->>(" + key + ")) "
        "THEN 'APPROVED_BOUND_EXPRESSION' ELSE 'UNSUPPORTED_BOUND_EXPRESSION' END "
        "ELSE " + value + " END"
    )


def installed_queries() -> tuple[str, str]:
    full = CATALOG_SQL.read_text()
    marker = ", acl_objects AS ("
    if full.count(marker) != 1:
        raise ValueError("Installed catalog template changed")
    rest = full.split(marker, 1)[1]
    prefix = (
        sql.SQL("""
      WITH current_db AS MATERIALIZED (
        SELECT * FROM pg_catalog.pg_database WHERE datname=current_database()
      ), temporary AS MATERIALIZED (
        SELECT oid FROM pg_catalog.pg_namespace
          WHERE oid=pg_my_temp_schema() OR pg_is_other_temp_schema(oid)
        UNION SELECT t.oid FROM pg_catalog.pg_namespace t
          JOIN pg_catalog.pg_namespace p ON t.nspname='pg_toast_'||substr(p.nspname,4)
          WHERE p.oid=pg_my_temp_schema() OR pg_is_other_temp_schema(p.oid)
      ), scope_ns AS MATERIALIZED (
        SELECT * FROM pg_catalog.pg_namespace WHERE
          nspname NOT IN ('pg_catalog','information_schema','pg_toast')
          AND oid NOT IN (SELECT oid FROM temporary)
      ), roles AS MATERIALIZED (
        SELECT r.oid,CASE WHEN r.oid=d.datdba THEN 'DATABASE_OWNER'
          WHEN r.oid=:owner THEN 'ERASURE_OWNER'
          WHEN r.oid=:authorizer THEN 'ERASURE_AUTHORIZER'
          WHEN r.oid=:executor THEN 'ERASURE_EXECUTOR'
          WHEN r.rolname=:retirement_owner THEN 'EXPORT_RETIREMENT_OWNER'
          WHEN r.rolname='pg_database_owner' THEN 'DATABASE_OWNER_ROLE'
          ELSE 'ROLE:'||r.rolname END AS label,
          jsonb_build_array(r.rolsuper,r.rolinherit,r.rolcreaterole,r.rolcreatedb,
            r.rolcanlogin,r.rolreplication,r.rolbypassrls,r.rolconnlimit,r.rolvaliduntil) AS flags
        FROM pg_catalog.pg_roles r CROSS JOIN current_db d
      ), rels AS MATERIALIZED (
        SELECT c.*,{ns}||'.'||c.relname AS qualified
          FROM pg_catalog.pg_class c JOIN scope_ns n ON n.oid=c.relnamespace
      ), funcs AS MATERIALIZED (
        SELECT p.*,p.oid::regprocedure::text AS signature FROM pg_catalog.pg_proc p
          JOIN scope_ns n ON n.oid=p.pronamespace
      ), types AS MATERIALIZED (
        SELECT t.*,{ns}||'.'||t.typname AS qualified
          FROM pg_catalog.pg_type t JOIN scope_ns n ON n.oid=t.typnamespace
      )
    """)
        .format(ns=sql.SQL(_namespace("n.oid", "n.nspname")))
        .as_string()
    )
    full = marker + rest
    raw = RAW_SQL.read_text()
    if full.count("'FUNCTION:'||signature") != 1:
        raise ValueError("Installed function ACL template changed")
    full = full.replace("'FUNCTION:'||signature", "'FUNCTION:'||" + _reference("signature"))
    # Canonicalize only explicit technical references. Apply before inserting any
    # live-body comparison, so prosrc never passes through this name renderer.
    references = {
        "p.signature",
        "a.atttypid::regtype::text",
        "p.prosupport::regprocedure::text",
        "p.prorettype::regtype::text",
        "x::regtype::text",
        "t.typelem::regtype::text",
        "t.typbasetype::regtype::text",
        "t.typrelid::regclass::text",
        "c.conrelid::regclass::text",
        "c.confrelid::regclass::text",
        "t.tgfoid::regprocedure::text",
        "i.inhrelid::regclass::text",
        "i.inhparent::regclass::text",
    }
    references.update(
        re.findall(r"\b[a-z]\.[a-z_]+::reg(?:procedure|type|class|operator|proc)::text", full + raw)
    )
    for reference in sorted(references, key=len, reverse=True):
        full = full.replace(reference, _reference(reference))
        raw = raw.replace(reference, _reference(reference))
    for name in ("full", "raw"):
        value = full if name == "full" else raw
        value = value.replace(
            "WHERE n.nspname='public'", "WHERE n.oid IN (SELECT oid FROM scope_ns)"
        )
        value = value.replace("WHERE nspname='public'", "WHERE oid IN (SELECT oid FROM scope_ns)")
        value = value.replace("n.nspname", _namespace("n.oid", "n.nspname"))
        value = value.replace("'SCHEMA:'||nspname", "'SCHEMA:'||" + _namespace("oid", "nspname"))
        if name == "full":
            full = value
        else:
            raw = value
    constraint_key = "'CONSTRAINT:'||COALESCE(r.qualified,t.qualified)||':'||c.conname"
    default_key = "'DEFAULT:'||c.qualified||':'||a.attname"
    for name, field in NODE_FIELDS.items():
        token = "__NODE_" + name + "__"
        if raw.count(token) != 1:
            raise ValueError("Installed raw template changed")
        expression = datum_sql(sql.Identifier(*field))
        if name in {"CONSTRAINT", "COLUMN_DEFAULT"}:
            expression = _expression(
                constraint_key if name == "CONSTRAINT" else default_key, expression
            )
        raw = raw.replace(token, expression)
    for token, key in (
        ("pg_get_constraintdef(c.oid,true)", constraint_key),
        ("pg_get_expr(d.adbin,d.adrelid,true)", default_key),
    ):
        if full.count(token) != 1:
            raise ValueError("Installed definition template changed")
        full = full.replace(
            token,
            "CASE WHEN CAST(:expression_hashes AS jsonb)?("
            + key
            + ") THEN 'APPROVED_BOUND_EXPRESSION' ELSE "
            + token
            + " END",
        )
    index = "pg_get_indexdef(i.indexrelid)"
    full = full.replace(
        index,
        "replace(replace(" + index + ",' ON '||quote_ident(:cap)||'.',' ON CAPABILITY.'),"
        "' ON '||quote_ident(:crypto)||'.',' ON CRYPTO.')",
    )
    for query in (full, raw):
        if query.count("__DYNAMIC_BODY__") != 1 or "__NODE_" in query:
            raise ValueError("Installed body template changed")
    return prefix + full.replace("__DYNAMIC_BODY__", _body()), prefix + raw.replace(
        "__DYNAMIC_BODY__", _body()
    )
