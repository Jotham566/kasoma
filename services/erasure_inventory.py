"""Read-only ADR-061 structural drift fence; never ownership/hold/execution clearance."""

from collections.abc import Mapping
from dataclasses import dataclass

from psycopg import sql
from sqlalchemy import Connection, text

from services.erasure_manifest import BASELINE, BASELINE_REVISION, SourceColumn


class SourceManifestChanged(ValueError):
    def __init__(self) -> None:
        super().__init__("SOURCE_MANIFEST_CHANGED")


@dataclass(frozen=True)
class ObservedSource:
    primary_key: tuple[str, ...]
    columns: tuple[SourceColumn, ...]
    relation_kind: str = "r"


def assert_baseline(revision: str, sources: Mapping[str, ObservedSource]) -> None:
    if revision != BASELINE_REVISION or sources.keys() != BASELINE.keys():
        raise SourceManifestChanged()
    for name, expected in BASELINE.items():
        actual = sources[name]
        if (
            actual.relation_kind != "r"
            or actual.primary_key != expected.primary_key
            or actual.columns != expected.columns
        ):
            raise SourceManifestChanged()


def check_source_shape(db: Connection) -> None:
    """Inspect only current-schema catalogs and its migration marker, never learner rows.

    The caller must still verify trigger definitions/privileges, payload versions,
    ownership, exact preservation and every other approved execution prerequisite.
    """
    schema = db.scalar(text("SELECT current_schema()"))
    if not isinstance(schema, str):
        raise SourceManifestChanged()
    rows = db.execute(
        text("""
          WITH scoped AS MATERIALIZED (
            SELECT c.oid,c.relname,c.relkind FROM pg_catalog.pg_class c
            WHERE c.relnamespace=pg_catalog.to_regnamespace(:schema)
              AND c.relkind IN ('r','p','f','m','v') ORDER BY c.relname LIMIT 72
          )
          SELECT s.relname,s.relkind,
            (SELECT array_agg(a.attname::text ORDER BY k.ordinality)
             FROM pg_catalog.pg_constraint p
             CROSS JOIN LATERAL unnest(p.conkey) WITH ORDINALITY k(attnum,ordinality)
             JOIN pg_catalog.pg_attribute a ON a.attrelid=p.conrelid AND a.attnum=k.attnum
             WHERE p.conrelid=s.oid AND p.contype='p') AS primary_key,
            (SELECT jsonb_agg(jsonb_build_array(a.attname,
                               CASE WHEN t.typnamespace='pg_catalog'::regnamespace
                                 THEN t.typname::text ELSE 'UNSUPPORTED_TYPE' END,
                               NOT a.attnotnull)
                             ORDER BY a.attnum)
             FROM (SELECT * FROM pg_catalog.pg_attribute
                   WHERE attrelid=s.oid AND attnum>0 AND NOT attisdropped
                   ORDER BY attnum LIMIT 502) a
             JOIN pg_catalog.pg_type t ON t.oid=a.atttypid) AS columns
          FROM scoped s ORDER BY s.relname
        """),
        {"schema": schema},
    ).all()
    if len(rows) != len(BASELINE):
        raise SourceManifestChanged()
    sources = {
        row.relname: ObservedSource(
            tuple(row.primary_key or ()),
            tuple(SourceColumn(name, kind, nullable) for name, kind, nullable in row.columns or ()),
            row.relkind,
        )
        for row in rows
    }
    # Never fall through a search_path to public's marker for an incomplete isolated schema.
    marker = sql.SQL("SELECT version_num FROM {}.alembic_version LIMIT 2").format(
        sql.Identifier(schema)
    )
    revisions = db.execute(text(marker.as_string())).all()
    if len(revisions) != 1:
        raise SourceManifestChanged()
    assert_baseline(revisions[0].version_num, sources)
