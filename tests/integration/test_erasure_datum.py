"""ADR-076 bit-preserving raw-tree codec and pre-deparser refusal."""

import pytest
from psycopg import sql
from sqlalchemy import event, text

from services.database import engine_for
from services.erasure_catalog import CatalogUnavailable, check_preinstall_catalog
from services.erasure_datum import DATUM_PATTERN, datum_sql
from tests.integration.test_erasure_capability import source

pytestmark = pytest.mark.integration


def test_signed_octets_preserve_bits_order_and_every_non_octet_tree_field():
    with source() as proof:
        engine = engine_for(proof.settings)
        try:
            with engine.begin() as db:
                query = text("SELECT " + datum_sql(sql.SQL(":node")))

                def canonical(node):
                    return db.scalar(query, {"node": node, "datum_pattern": DATUM_PATTERN})

                signed = "{CONST :location -1 :constvalue 4 [ -24 3 0 0 -128 -1 127 0 ]}"
                unsigned = "{CONST :location -1 :constvalue 4 [ 232 3 0 0 128 255 127 0 ]}"
                assert canonical(signed) == unsigned
                assert canonical(unsigned) == unsigned
                assert canonical(signed + signed) == unsigned + unsigned
                assert canonical(None) is None
                assert canonical("{CONST :constvalue <>}") == "{CONST :constvalue <>}"
                assert canonical("{CONST :constvalue 0 [ ]}") == "{CONST :constvalue 0 [ ]}"
                for changed in (
                    unsigned.replace("232", "233"),
                    unsigned.replace("232 3", "3 232"),
                    unsigned.replace("location -1", "location 255"),
                    unsigned.replace("constvalue 4", "constvalue 8"),
                ):
                    assert canonical(changed) != canonical(unsigned)
                for invalid in ("256", "-129"):
                    result = canonical("{CONST :constvalue 1 [ " + invalid + " ]}")
                    assert "INVALID_OCTET" in result
                    assert result != canonical("{CONST :constvalue 1 [ 0 ]}")
                escaped = r"token\ :constvalue\ 4\ [\ -24\ ]"
                assert canonical(escaped) == escaped
        finally:
            engine.dispose()


def test_same_length_constant_drift_is_rejected_before_any_full_deparser():
    with source() as proof:
        engine = engine_for(proof.settings)
        stages = []

        def observed(conn, cursor, statement, parameters, context, executemany):
            if "raw_objects(category,body)" in statement:
                stages.append("RAW")
            elif "acl_objects AS (" in statement:
                stages.append("FULL")

        try:
            with engine.begin() as db:
                check_preinstall_catalog(db)
                db.execute(text("ALTER TABLE public.users DROP CONSTRAINT users_closed_disabled"))
                db.execute(
                    text(
                        "ALTER TABLE public.users ADD CONSTRAINT users_closed_disabled "
                        "CHECK (closed_at IS NULL OR status='DISABLEE')"
                    )
                )
                event.listen(engine, "before_cursor_execute", observed)
                try:
                    with pytest.raises(CatalogUnavailable):
                        check_preinstall_catalog(db)
                    assert stages == ["RAW"]
                finally:
                    event.remove(engine, "before_cursor_execute", observed)
        finally:
            engine.dispose()
