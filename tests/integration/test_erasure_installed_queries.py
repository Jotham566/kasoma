"""Independent raw/full metadata reproduction, not installed v7 clearance."""

import pytest
from psycopg import sql
from sqlalchemy import text

from scripts.erasure_capability import CapabilityInstallUnavailable, prepare_catalog
from scripts.erasure_installed_profile import observe_prepared
from services.database import engine_for
from tests.integration.test_erasure_capability import source
from tests.integration.test_erasure_catalog_preparation import unchanged

pytestmark = pytest.mark.integration


def test_installed_metadata_reproduces_across_two_rolled_back_preparations():
    observations, templates = [], {}
    for varied in (False, True):
        with source() as proof:
            if varied:
                engine = engine_for(proof.settings)
                try:
                    with engine.begin() as db:
                        db.execute(text("CREATE TEMP TABLE kasoma_metadata_offset(id integer)"))
                finally:
                    engine.dispose()

            def collect(db, bindings, definitions):
                snapshot = observe_prepared(db, bindings, definitions, templates or None)
                templates.update(snapshot.expressions)
                observations.append((bindings, snapshot))

            prepare_catalog(proof, collect)
    assert observations[0][0].owner_oid != observations[1][0].owner_oid
    assert observations[0][0].installation_nonce != observations[1][0].installation_nonce
    assert observations[0][1] == observations[1][1]


def test_preparation_rejects_changed_complete_body_before_metadata_observation():
    with source() as proof:
        engine = engine_for(proof.settings)
        try:
            with engine.connect() as db:
                before = db.execute(
                    text("SELECT to_jsonb(s) FROM public.account_erasure_state s")
                ).one()
            reached = []

            def collect(db, bindings, definitions):
                # Approved interface and an innocuous result still cannot replace
                # the complete independently compiled expected body.
                replacement = sql.SQL(
                    "CREATE OR REPLACE FUNCTION {}.scope_identity_ok() RETURNS boolean "
                    "LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog "
                    "AS $$ SELECT false $$"
                ).format(sql.Identifier(bindings.namespace))
                db.execute(text(replacement.as_string()))
                with pytest.raises(ValueError, match="Prepared code did not match"):
                    observe_prepared(db, bindings, definitions)
                reached.append(True)
                raise ValueError("SYNTHETIC_CHANGED_BODY")

            with pytest.raises(CapabilityInstallUnavailable) as rejected:
                prepare_catalog(proof, collect)
            assert rejected.value.phase == "DEFINITION"
            assert reached == [True]
            unchanged(engine, before, proof.nonce)
        finally:
            engine.dispose()
