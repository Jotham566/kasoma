"""Independent fresh-source raw metadata, never a runtime source baseline."""

import pytest
from psycopg import sql
from sqlalchemy import text

from scripts.erasure_capability import install
from services.database import engine_for
from services.erasure_catalog_bindings import BOUND_EXPRESSIONS, CatalogBindings, freeze_expression
from services.erasure_datum import DATUM_PATTERN, datum_sql
from tests.integration.test_erasure_capability import source

pytestmark = pytest.mark.integration


def snapshot(proof, *, consume_oid=False):
    engine = engine_for(proof.settings)
    try:
        if consume_oid:
            with engine.begin() as db:
                db.execute(text("CREATE TEMP TABLE kasoma_catalog_offset(id integer)"))
        capability = install(proof)
        with engine.begin() as db:
            creator = db.scalar(
                text("SELECT datdba FROM pg_catalog.pg_database WHERE datname=current_database()")
            )
            values = CatalogBindings(
                proof.database_oid,
                proof.namespace_oid,
                capability.owner_oid,
                capability.authorizer_oid,
                capability.executor_oid,
                creator,
                proof.nonce,
            )
            rows = (
                db.execute(
                    text(
                        "SELECT 'CONSTRAINT:'||CASE WHEN n.nspname='public' THEN "
                        "'public.account_erasure_state' ELSE 'CAPABILITY.control' "
                        "END||':'||c.conname AS key,"
                        + datum_sql(sql.Identifier("c", "conbin"))
                        + " AS tree "
                        "FROM pg_catalog.pg_constraint c JOIN pg_catalog.pg_namespace n "
                        "ON n.oid=c.connamespace WHERE n.nspname=:cap OR "
                        "(n.nspname='public' AND c.conname='account_erasure_state_bound_owner')"
                    ),
                    {"cap": capability.namespace, "datum_pattern": DATUM_PATTERN},
                )
                .mappings()
                .all()
            )
            rows += (
                db.execute(
                    text(
                        "SELECT 'DEFAULT:CAPABILITY.control:'||a.attname AS key,"
                        + datum_sql(sql.Identifier("d", "adbin"))
                        + " AS tree "
                        "FROM pg_catalog.pg_attrdef d JOIN pg_catalog.pg_class c "
                        "ON c.oid=d.adrelid "
                        "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
                        "JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid AND a.attnum=d.adnum "
                        "WHERE n.nspname=:cap"
                    ),
                    {"cap": capability.namespace, "datum_pattern": DATUM_PATTERN},
                )
                .mappings()
                .all()
            )
            selected = {row["key"]: row["tree"] for row in rows if row["key"] in BOUND_EXPRESSIONS}
            assert selected.keys() == BOUND_EXPRESSIONS.keys()
            assert tuple(
                db.execute(
                    text("SELECT 0000000010=10,0000016384=16384,pg_typeof(0000016384)::text")
                ).one()
            ) == (True, True, "integer")
            return values, selected
    finally:
        engine.dispose()


def test_all_ten_templates_reproduce_a_separate_owned_source_with_new_bindings():
    with source() as first:
        original, trees = snapshot(first)
    frozen = {key: freeze_expression(key, tree, original) for key, tree in trees.items()}
    with source() as second:
        varied, observed = snapshot(second, consume_oid=True)
    assert original.owner_oid != varied.owner_oid
    assert original.installation_nonce != varied.installation_nonce
    assert original.namespace != varied.namespace
    assert {key: template.render(varied) for key, template in frozen.items()} == observed
