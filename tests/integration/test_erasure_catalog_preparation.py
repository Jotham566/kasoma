"""ADR-079 prepared metadata is not an installed capability or execution authority."""

import pytest
from psycopg import sql
from sqlalchemy import text

from scripts.erasure_capability import CapabilityInstallUnavailable, prepare_catalog
from scripts.erasure_catalog_code import expected_code_hashes
from services.database import engine_for
from services.erasure_catalog import check_preinstall_catalog
from tests.integration.test_erasure_capability import source

pytestmark = pytest.mark.integration


def unchanged(engine, before, nonce):
    with engine.connect() as db:
        after = db.execute(text("SELECT to_jsonb(s) FROM public.account_erasure_state s")).one()
        assert after == before
        assert db.scalar(text("SELECT count(*) FROM public.account_erasure_jobs")) == 0
        assert db.scalar(text("SELECT count(*) FROM public.account_erasure_plans")) == 0
        assert not db.scalar(
            text(
                "SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_namespace "
                "WHERE nspname IN (:cap,:crypto))"
            ),
            {"cap": "kasoma_cap_" + nonce.hex, "crypto": "kasoma_ec_" + nonce.hex},
        )
        assert not db.scalar(
            text(
                "SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_roles "
                "WHERE rolname IN (:owner,:author,:executor))"
            ),
            {
                "owner": "kasoma_eo_" + nonce.hex,
                "author": "kasoma_ea_" + nonce.hex,
                "executor": "kasoma_ex_" + nonce.hex,
            },
        )
        assert not db.scalar(
            text("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_extension WHERE extname='pgcrypto')")
        )
        check_preinstall_catalog(db)


@pytest.mark.parametrize("outcome", ["RETURN", "ERROR", "INTERRUPT"])
def test_preparation_never_initializes_or_hands_off_and_rolls_back_every_private_definition(
    outcome,
):
    with source() as proof:
        engine = engine_for(proof.settings)
        observations = []
        try:
            with engine.connect() as db:
                before = db.execute(
                    text("SELECT to_jsonb(s) FROM public.account_erasure_state s")
                ).one()

            def collect(db, bindings, definitions):
                assert bindings.namespace == "kasoma_cap_" + proof.nonce.hex
                control = sql.SQL("SELECT count(*) FROM {}.control").format(
                    sql.Identifier(bindings.namespace)
                )
                assert db.scalar(text(control.as_string())) == 0
                # Only a boolean leaves PostgreSQL even if clearing regresses.
                assert (
                    db.scalar(
                        text(
                            "SELECT coalesce(length(current_setting("
                            "'kasoma.bootstrap_password',true)),0)=0"
                        )
                    )
                    is True
                )
                assert (
                    db.scalar(
                        text(
                            "SELECT NOT original_scope_eligible AND NOT creation_enabled "
                            "AND NOT execution_enabled FROM public.account_erasure_state"
                        )
                    )
                    is True
                )
                assert any("scope_identity_ok" in definition for definition in definitions)
                database = db.scalar(text("SELECT current_database()"))
                expected = expected_code_hashes(bindings, database, definitions)
                assert len(expected) == 14
                # Compare complete live bodies in PostgreSQL; only booleans leave.
                for name, digest in expected.items():
                    assert (
                        db.scalar(
                            text(
                                "SELECT encode(sha256(convert_to(prosrc,'UTF8')),'hex')=:digest "
                                "FROM pg_catalog.pg_proc WHERE oid=CAST(:name AS regprocedure)"
                            ),
                            {"name": name, "digest": digest},
                        )
                        is True
                    )
                observations.append(True)
                if outcome == "ERROR":
                    raise ValueError("SYNTHETIC_METADATA_COLLECTOR_FAILURE")
                if outcome == "INTERRUPT":
                    raise KeyboardInterrupt()

            if outcome == "ERROR":
                with pytest.raises(CapabilityInstallUnavailable) as rejected:
                    prepare_catalog(proof, collect)
                assert rejected.value.phase == "DEFINITION"
            elif outcome == "INTERRUPT":
                with pytest.raises(KeyboardInterrupt):
                    prepare_catalog(proof, collect)
            else:
                assert prepare_catalog(proof, collect) is None
            assert observations == [True]
            unchanged(engine, before, proof.nonce)
        finally:
            engine.dispose()
