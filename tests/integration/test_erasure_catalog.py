"""ADR-073 actual fresh-source catalog drift; no review/real-data erasure."""

from uuid import uuid4

import pytest
from sqlalchemy import event, text

from scripts.erasure_capability import CapabilityInstallUnavailable, install
from services.database import engine_for
from services.erasure_catalog import (
    CatalogUnavailable,
    check_preinstall_catalog,
    load_baseline,
    observe_catalog,
)
from services.erasure_inventory import check_source_shape
from tests.integration.test_erasure_capability import source

pytestmark = pytest.mark.integration


def test_body_only_drift_must_be_refused_before_private_bootstrap():
    with source() as proof:
        engine = engine_for(proof.settings)
        try:
            with engine.begin() as db:
                check_preinstall_catalog(db)
                db.execute(
                    text("""
                  CREATE OR REPLACE FUNCTION public.account_erasure_closure_guard()
                  RETURNS trigger LANGUAGE plpgsql AS $$
                  BEGIN
                    -- SYNTHETIC_CATALOG_CANARY_MUST_NOT_ESCAPE
                    RETURN NEW;
                  END $$
                """)
                )
                check_source_shape(db)  # Columns/PKs alone cannot detect this change.
                stages = []

                def observed(conn, cursor, statement, parameters, context, executemany):
                    if "raw_objects(category,body)" in statement:
                        stages.append("RAW")
                    elif "acl_objects AS (" in statement:
                        stages.append("FULL")

                event.listen(engine, "before_cursor_execute", observed)
                try:
                    with pytest.raises(CatalogUnavailable) as denied:
                        check_preinstall_catalog(db)
                    assert str(denied.value) == "ERASURE_CATALOG_UNAVAILABLE"
                    assert stages == ["RAW"]
                    assert db.scalar(text("SELECT current_schema()")) == "public"
                finally:
                    event.remove(engine, "before_cursor_execute", observed)
            with pytest.raises(CapabilityInstallUnavailable) as failure:
                install(proof)
            assert failure.value.phase == "SOURCE"
            with engine.connect() as db:
                assert db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) == 0
                assert (
                    db.scalar(text("SELECT original_scope_eligible FROM account_erasure_state"))
                    is False
                )
                assert (
                    db.scalar(
                        text("SELECT count(*) FROM pg_catalog.pg_roles WHERE rolname=ANY(:roles)"),
                        {
                            "roles": [
                                "kasoma_eo_" + proof.nonce.hex,
                                "kasoma_ea_" + proof.nonce.hex,
                                "kasoma_ex_" + proof.nonce.hex,
                            ]
                        },
                    )
                    == 0
                )
        finally:
            engine.dispose()


def test_fresh_metadata_matches_after_row_writes_and_restores_connection_settings():
    expected = load_baseline()
    for _ in range(2):
        with source() as proof:
            engine = engine_for(proof.settings)
            try:
                with engine.begin() as db:
                    db.execute(text("SET LOCAL search_path=public,pg_catalog"))
                    db.execute(text("SET LOCAL timezone='Pacific/Auckland'"))
                    db.execute(text("SET LOCAL statement_timeout='7000ms'"))
                    db.execute(text("SET LOCAL lock_timeout='900ms'"))
                    before = tuple(
                        db.scalar(text("SHOW " + setting))
                        for setting in (
                            "search_path",
                            "timezone",
                            "statement_timeout",
                            "lock_timeout",
                        )
                    )
                    assert observe_catalog(db) == expected
                    db.execute(
                        text(
                            "INSERT INTO public.users(id,status,created_at) "
                            "VALUES(:user,'ACTIVE',clock_timestamp())"
                        ),
                        {"user": uuid4()},
                    )
                    assert observe_catalog(db) == expected
                    after = tuple(
                        db.scalar(text("SHOW " + setting))
                        for setting in (
                            "search_path",
                            "timezone",
                            "statement_timeout",
                            "lock_timeout",
                        )
                    )
                    assert before == after
                    check_preinstall_catalog(db)
            finally:
                engine.dispose()


def mutate_catalog(db, change):
    from psycopg import sql

    from services.erasure_catalog import retirement_owner

    fixed = {
        "TRIGGER_DISABLED": "ALTER TABLE public.users DISABLE TRIGGER users_erasure_closure",
        "CHECK_DROP": "ALTER TABLE public.users DROP CONSTRAINT users_closed_disabled",
        "FUNCTION_SECURITY": (
            "ALTER FUNCTION public.account_erasure_closure_guard() SECURITY DEFINER"
        ),
        "FUNCTION_SETTING": (
            "ALTER FUNCTION public.account_erasure_closure_guard() "
            "SET search_path=public,pg_catalog"
        ),
        "TABLE_GRANT": "GRANT SELECT ON public.users TO PUBLIC",
        "COLUMN_GRANT": "GRANT UPDATE(display_name) ON public.users TO PUBLIC",
        "DEFAULT_GRANT": (
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO PUBLIC"
        ),
        "RLS": "ALTER TABLE public.users ENABLE ROW LEVEL SECURITY",
        "POLICY": "CREATE POLICY synthetic_catalog ON public.users USING (true)",
        "ROLE": "CREATE ROLE kasoma_er_untrusted NOLOGIN NOINHERIT",
        "RULE": "CREATE RULE synthetic_catalog AS ON DELETE TO public.users DO INSTEAD NOTHING",
        "TYPE": "CREATE TYPE public.synthetic_catalog AS ENUM ('UNKNOWN')",
        "OPERATOR": (
            "ALTER OPERATOR public.= (public.vector,public.vector) SET (RESTRICT=pg_catalog.neqsel)"
        ),
        "DEFAULT": (
            "ALTER TABLE public.users ALTER COLUMN created_at "
            "SET DEFAULT '2000-01-01T00:00:00Z'::timestamptz"
        ),
    }
    if change in fixed:
        db.execute(text(fixed[change]))
    elif change == "FK_DROP":
        name = db.scalar(
            text("""
          SELECT conname FROM pg_catalog.pg_constraint
          WHERE conrelid='public.user_identifiers'::regclass
            AND contype='f' ORDER BY conname LIMIT 1
        """)
        )
        assert name
        db.execute(
            text(
                sql.SQL("ALTER TABLE public.user_identifiers DROP CONSTRAINT {}")
                .format(sql.Identifier(name))
                .as_string()
            )
        )
    elif change == "INDEX_DROP":
        name = db.scalar(
            text("""
          SELECT c.relname FROM pg_catalog.pg_index i
          JOIN pg_catalog.pg_class c ON c.oid=i.indexrelid
          JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public'
            AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_constraint k WHERE k.conindid=c.oid)
          ORDER BY c.relname LIMIT 1
        """)
        )
        assert name
        db.execute(text(sql.SQL("DROP INDEX public.{}").format(sql.Identifier(name)).as_string()))
    elif change == "OWNER_LOGIN":
        name = retirement_owner(db.scalar(text("SELECT current_database()")))
        db.execute(text(sql.SQL("ALTER ROLE {} LOGIN").format(sql.Identifier(name)).as_string()))
    elif change == "BODY_PLACEHOLDER":
        # This must not be normalized into the expected derived role at verification time.
        body = load_baseline().body_templates["export_retirement_owner_safe"]
        db.execute(
            text(
                sql.SQL(
                    "CREATE OR REPLACE FUNCTION public.export_retirement_owner_safe() "
                    "RETURNS boolean LANGUAGE sql STABLE SET search_path=pg_catalog AS {}"
                )
                .format(sql.Literal(body))
                .as_string()
            )
        )
    else:
        raise AssertionError("Unsupported closed mutation")


@pytest.mark.parametrize(
    "change",
    [
        "TRIGGER_DISABLED",
        "CHECK_DROP",
        "FUNCTION_SECURITY",
        "FUNCTION_SETTING",
        "TABLE_GRANT",
        "COLUMN_GRANT",
        "DEFAULT_GRANT",
        "RLS",
        "POLICY",
        "ROLE",
        "RULE",
        "TYPE",
        "OPERATOR",
        "DEFAULT",
        "FK_DROP",
        "INDEX_DROP",
        "OWNER_LOGIN",
        "BODY_PLACEHOLDER",
    ],
)
def test_behavior_or_privilege_drift_is_refused_without_creating_principals(change):
    with source() as proof:
        engine = engine_for(proof.settings)
        try:
            with engine.begin() as db:
                check_preinstall_catalog(db)
                mutate_catalog(db, change)
                check_source_shape(db)
                with pytest.raises(CatalogUnavailable):
                    check_preinstall_catalog(db)
            with pytest.raises(CapabilityInstallUnavailable) as failed:
                install(proof)
            assert failed.value.phase == "SOURCE"
            with engine.connect() as db:
                assert (
                    db.scalar(text("SELECT original_scope_eligible FROM account_erasure_state"))
                    is False
                )
                assert (
                    db.scalar(
                        text(
                            "SELECT count(*) FROM pg_catalog.pg_namespace WHERE nspname=:namespace"
                        ),
                        {"namespace": "kasoma_cap_" + proof.nonce.hex},
                    )
                    == 0
                )
        finally:
            engine.dispose()
