"""Installed principal separation only; no full catalog or erasure clearance."""

import pytest
from psycopg import sql
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from tests.integration.test_erasure_plans import issue, planned_source, reviewed_case

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "drift",
    [
        "TABLE",
        "COLUMN",
        "PUBLIC_TABLE",
        "SCHEMA",
        "PUBLIC_FUNCTION",
        "LOST_SELECT",
        "SETTING",
        "GRANT_OPTION",
        "PUBLIC_COLUMN",
        "PUBLIC_CREATE",
        "LOST_COLUMN",
        "CRYPTO",
        "TYPE",
        "PRIVATE_HELPER",
        "DATABASE",
        "DEFAULT",
        "MEMBERSHIP",
        "OWNER_FLAGS",
        "VALID_UNTIL",
        "PERSISTENT_OWNER",
        "THIRD_PARTY",
    ],
)
def test_installed_principal_drift_refuses_all_entrypoints_without_source_writes(drift):
    with planned_source() as (proof, capability, identity, authorizer, executor):
        _, admin, case = reviewed_case(identity)
        with identity.engine.begin() as db:
            roles = dict(db.execute(text("SELECT oid,rolname FROM pg_catalog.pg_roles")).all())
            owner = sql.Identifier(roles[capability.owner_oid])
            author = sql.Identifier(roles[capability.authorizer_oid])
            worker = sql.Identifier(roles[capability.executor_oid])
            cap = sql.Identifier(capability.namespace)
            crypto = sql.Identifier(capability.namespace.replace("kasoma_cap_", "kasoma_ec_", 1))
            database = sql.Identifier(db.scalar(text("SELECT current_database()")))
            choices = {
                "TABLE": sql.SQL("GRANT SELECT ON public.users TO {}").format(author),
                "COLUMN": sql.SQL("GRANT UPDATE(display_name) ON public.users TO {}").format(
                    worker
                ),
                "PUBLIC_TABLE": sql.SQL("GRANT SELECT ON public.users TO PUBLIC"),
                "SCHEMA": sql.SQL("GRANT CREATE ON SCHEMA {} TO {}").format(cap, author),
                "PUBLIC_FUNCTION": sql.SQL(
                    "GRANT EXECUTE ON FUNCTION {}.readiness() TO PUBLIC"
                ).format(cap),
                "LOST_SELECT": sql.SQL("REVOKE SELECT ON public.attempts FROM {}").format(owner),
                "SETTING": sql.SQL("ALTER ROLE {} SET lock_timeout='1000ms'").format(author),
                "GRANT_OPTION": sql.SQL(
                    "GRANT EXECUTE ON FUNCTION {}.readiness() TO {} WITH GRANT OPTION"
                ).format(cap, worker),
                "PUBLIC_COLUMN": sql.SQL("GRANT SELECT(display_name) ON public.users TO PUBLIC"),
                "PUBLIC_CREATE": sql.SQL("GRANT CREATE ON SCHEMA public TO PUBLIC"),
                "LOST_COLUMN": sql.SQL("REVOKE UPDATE(id) ON public.users FROM {}").format(owner),
                "CRYPTO": sql.SQL(
                    "GRANT EXECUTE ON FUNCTION {}.hmac(bytea,bytea,text) TO {}"
                ).format(crypto, author),
                "TYPE": sql.SQL("GRANT USAGE ON TYPE public.vector TO {}").format(author),
                "PRIVATE_HELPER": sql.SQL(
                    "GRANT EXECUTE ON FUNCTION {}.principal_acl_ok() TO {}"
                ).format(cap, worker),
                "DATABASE": sql.SQL("GRANT CREATE ON DATABASE {} TO {}").format(database, author),
                "DEFAULT": sql.SQL("ALTER DEFAULT PRIVILEGES GRANT SELECT ON TABLES TO {}").format(
                    author
                ),
                "MEMBERSHIP": sql.SQL(
                    "CREATE ROLE kasoma_acl_peer NOLOGIN; GRANT kasoma_acl_peer TO {}"
                ).format(author),
                "OWNER_FLAGS": sql.SQL("ALTER ROLE {} CREATEROLE").format(owner),
                "VALID_UNTIL": sql.SQL("ALTER ROLE {} VALID UNTIL '2030-01-01 00:00:00+00'").format(
                    author
                ),
                "PERSISTENT_OWNER": sql.SQL(
                    "CREATE TABLE {}.extra(id integer); ALTER TABLE {}.extra OWNER TO {}; "
                    "REVOKE ALL ON {}.extra FROM {};"
                ).format(cap, cap, owner, cap, owner),
                "THIRD_PARTY": sql.SQL(
                    "CREATE ROLE kasoma_acl_peer NOLOGIN; "
                    "GRANT EXECUTE ON FUNCTION {}.principal_acl_ok() TO kasoma_acl_peer"
                ).format(cap),
            }
            db.execute(text(choices[drift].as_string()))
            before = db.execute(
                text(
                    "SELECT (SELECT count(*) FROM account_erasure_plans),"
                    "(SELECT count(*) FROM audit_log),"
                    "(SELECT count(*) FROM account_erasure_jobs)"
                )
            ).one()
        for engine, function in [
            (authorizer, "readiness"),
            (executor, "readiness"),
            (executor, "expire_plans"),
        ]:
            with pytest.raises(DBAPIError) as rejected, engine.begin() as db:
                db.execute(
                    text(
                        sql.SQL("SELECT {}.{}()").format(cap, sql.Identifier(function)).as_string()
                    )
                )
            assert rejected.value.orig.sqlstate == "42501"
        with pytest.raises(DBAPIError) as rejected:
            issue(proof, capability, authorizer, admin[1], case)
        assert rejected.value.orig.sqlstate == "42501"
        with identity.engine.connect() as db:
            assert (
                db.execute(
                    text(
                        "SELECT (SELECT count(*) FROM account_erasure_plans),"
                        "(SELECT count(*) FROM audit_log),"
                        "(SELECT count(*) FROM account_erasure_jobs)"
                    )
                ).one()
                == before
            )
