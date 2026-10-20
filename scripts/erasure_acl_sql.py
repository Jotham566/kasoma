"""ADR-078 fixed grant expectations; never learn authority from live ACLs."""

import re

from psycopg import sql

from services.erasure_manifest import BASELINE

FUNCTIONS = (
    "control_guard()",
    "initialize_control(bytea)",
    "scope_identity_ok()",
    "readiness()",
    "source_shape_ok()",
    "source_version(uuid,uuid)",
    "issue_plan(uuid,uuid,oid,oid,uuid,uuid)",
    "expire_plans()",
    "principal_acl_ok()",
)
TABLE_PRIVILEGES = ("INSERT", "SELECT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")


def compile_principal_fence(
    namespace: str, crypto: str, owner: int, authorizer: int, executor: int, creator: int
) -> str:
    if (
        re.fullmatch(r"kasoma_cap_[0-9a-f]{32}", namespace) is None
        or crypto != namespace.replace("kasoma_cap_", "kasoma_ec_", 1)
        or any(
            type(value) is not int or not 0 < value < 2**32
            for value in (owner, authorizer, executor, creator)
        )
        or len({owner, authorizer, executor, creator}) != 4
    ):
        raise ValueError("Invalid closed principal recipe")
    expected = []

    def oid(value: int) -> sql.Composable:
        return sql.SQL("{}::oid").format(sql.Literal(value))

    def object_id(kind: str, name: str) -> sql.Composable:
        converters = {"RELATION": "regclass", "FUNCTION": "regprocedure", "TYPE": "regtype"}
        return sql.SQL("{}::{}::oid").format(sql.Literal(name), sql.SQL(converters[kind]))

    def grant(
        kind: str,
        obj: sql.Composable,
        grantee: int,
        grantor: sql.Composable,
        privilege: str,
        subobject: sql.Composable | None = None,
    ) -> None:
        expected.append(
            sql.SQL("({},{},{},{},{},{},false)").format(
                sql.Literal(kind),
                obj,
                subobject if subobject is not None else sql.SQL("0::integer"),
                oid(grantee),
                grantor,
                sql.Literal(privilege),
            )
        )

    for name in BASELINE:
        grant("RELATION", object_id("RELATION", "public." + name), owner, oid(creator), "SELECT")
    for name, rights in {
        "account_erasure_state": ("UPDATE",),
        "account_erasure_plans": ("INSERT", "UPDATE", "DELETE"),
        "audit_log": ("INSERT",),
    }.items():
        for right in rights:
            grant("RELATION", object_id("RELATION", "public." + name), owner, oid(creator), right)
    control = object_id("RELATION", namespace + ".control")
    control_toast = sql.SQL("(SELECT reltoastrelid FROM pg_catalog.pg_class WHERE oid={})").format(
        control
    )
    for right in TABLE_PRIVILEGES:
        grant("RELATION", control, owner, oid(owner), right)
        grant("RELATION", control_toast, owner, oid(owner), right)
    for name, column in (
        ("auth_sessions", "id"),
        ("users", "id"),
        ("data_subject_requests", "id"),
        ("user_roles", "user_id"),
        ("data_request_reviews", "request_id"),
    ):
        relation = object_id("RELATION", "public." + name)
        attribute = sql.SQL(
            "(SELECT attnum::integer FROM pg_catalog.pg_attribute "
            "WHERE attrelid={} AND attname={} AND NOT attisdropped)"
        ).format(relation, sql.Literal(column))
        grant("COLUMN", relation, owner, oid(creator), "UPDATE", attribute)
    for function in FUNCTIONS:
        grant(
            "FUNCTION",
            object_id("FUNCTION", namespace + "." + function),
            owner,
            oid(owner),
            "EXECUTE",
        )
    for role, names in (
        (authorizer, ("readiness()", "issue_plan(uuid,uuid,oid,oid,uuid,uuid)")),
        (executor, ("readiness()", "expire_plans()")),
    ):
        for name in names:
            grant(
                "FUNCTION",
                object_id("FUNCTION", namespace + "." + name),
                role,
                oid(owner),
                "EXECUTE",
            )
    grant(
        "FUNCTION",
        object_id("FUNCTION", crypto + ".hmac(bytea,bytea,text)"),
        owner,
        oid(creator),
        "EXECUTE",
    )
    public_owner = sql.SQL("'pg_database_owner'::regrole::oid")
    for name, role, grantor, rights in (
        ("public", 0, public_owner, ("USAGE",)),
        ("public", owner, public_owner, ("USAGE",)),
        (namespace, owner, oid(owner), ("USAGE", "CREATE")),
        (namespace, authorizer, oid(owner), ("USAGE",)),
        (namespace, executor, oid(owner), ("USAGE",)),
        (crypto, creator, oid(creator), ("USAGE", "CREATE")),
        (crypto, owner, oid(creator), ("USAGE",)),
    ):
        schema_object = sql.SQL(
            "(SELECT oid FROM pg_catalog.pg_namespace WHERE nspname={})"
        ).format(sql.Literal(name))
        for right in rights:
            grant("SCHEMA", schema_object, role, grantor, right)
    for name in ("control", "_control"):
        type_object = object_id("TYPE", namespace + "." + name)
        for role in (owner, 0):
            grant("TYPE", type_object, role, oid(owner), "USAGE")
    database = sql.SQL("(SELECT oid FROM pg_catalog.pg_database WHERE datname=current_database())")
    for right in ("CONNECT", "TEMPORARY"):
        grant("DATABASE", database, 0, oid(creator), right)
    definition = sql.SQL("""
      CREATE FUNCTION {cap}.principal_acl_ok() RETURNS boolean LANGUAGE sql STABLE
      SET search_path=pg_catalog SET timezone='UTC' AS $body$
      WITH principals AS MATERIALIZED (SELECT ARRAY[{owner},{authorizer},{executor}]::oid[] AS ids),
      temporary AS MATERIALIZED (SELECT oid FROM pg_catalog.pg_namespace
        WHERE oid=pg_my_temp_schema() OR pg_is_other_temp_schema(oid)),
      control_relations AS MATERIALIZED (
        SELECT c.oid FROM pg_catalog.pg_class c WHERE c.oid={control}
        UNION ALL SELECT conindid FROM pg_catalog.pg_constraint
          WHERE conrelid={control} AND contype='p' AND conname='control_pkey'
        UNION ALL SELECT reltoastrelid FROM pg_catalog.pg_class WHERE oid={control}
        UNION ALL SELECT i.indexrelid FROM pg_catalog.pg_index i
          JOIN pg_catalog.pg_class c ON c.reltoastrelid=i.indrelid WHERE c.oid={control}
      ),
      expected(kind,object,subobject,grantee,grantor,privilege,grantable) AS (VALUES {expected}),
      actual(kind,object,subobject,grantee,grantor,privilege,grantable) AS MATERIALIZED (
        SELECT 'RELATION',c.oid,0,x.grantee,x.grantor,x.privilege_type,x.is_grantable
          FROM pg_catalog.pg_class c CROSS JOIN principals p
          CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl,acldefault(
            CASE WHEN c.relkind='S' THEN 'S' ELSE 'r' END::"char",c.relowner))) x
          WHERE c.relkind IN ('r','p','v','m','f','S','t') AND c.relpersistence<>'t'
            AND (x.grantee=ANY(p.ids) OR c.relnamespace={cap_oid}
              OR c.oid IN (SELECT oid FROM control_relations)
              OR (x.grantee=0 AND c.relnamespace='public'::regnamespace))
        UNION ALL SELECT 'COLUMN',c.oid,a.attnum::integer,x.grantee,x.grantor,
          x.privilege_type,x.is_grantable FROM pg_catalog.pg_class c
          JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid AND a.attnum>0
          CROSS JOIN principals p CROSS JOIN LATERAL aclexplode(a.attacl) x
          WHERE c.relpersistence<>'t' AND (x.grantee=ANY(p.ids)
            OR c.relnamespace={cap_oid} OR c.oid IN (SELECT oid FROM control_relations)
            OR (x.grantee=0 AND c.relnamespace='public'::regnamespace))
        UNION ALL SELECT 'FUNCTION',f.oid,0,x.grantee,x.grantor,x.privilege_type,x.is_grantable
          FROM pg_catalog.pg_proc f CROSS JOIN principals p
          CROSS JOIN LATERAL aclexplode(COALESCE(f.proacl,acldefault('f',f.proowner))) x
          WHERE f.pronamespace NOT IN (SELECT oid FROM temporary)
            AND (x.grantee=ANY(p.ids) OR f.pronamespace={cap_oid}
              OR (f.pronamespace={crypto_oid} AND x.grantee<>{creator})
              OR (x.grantee=0 AND f.oid IN (
                'public.account_erasure_dormant_guard()'::regprocedure,
                'public.account_erasure_closure_guard()'::regprocedure)))
        UNION ALL SELECT 'SCHEMA',n.oid,0,x.grantee,x.grantor,x.privilege_type,x.is_grantable
          FROM pg_catalog.pg_namespace n CROSS JOIN principals p
          CROSS JOIN LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) x
          WHERE n.oid NOT IN (SELECT oid FROM temporary)
            AND (x.grantee=ANY(p.ids) OR n.oid IN ({cap_oid},{crypto_oid})
              OR (x.grantee=0 AND n.nspname='public'))
        UNION ALL SELECT 'TYPE',t.oid,0,x.grantee,x.grantor,x.privilege_type,x.is_grantable
          FROM pg_catalog.pg_type t CROSS JOIN principals p
          CROSS JOIN LATERAL aclexplode(COALESCE(t.typacl,acldefault('T',t.typowner))) x
          WHERE t.typnamespace NOT IN (SELECT oid FROM temporary)
            AND (x.grantee=ANY(p.ids) OR t.typnamespace={cap_oid}
              OR (t.typnamespace={crypto_oid} AND x.grantee<>{creator}))
        UNION ALL SELECT 'DATABASE',d.oid,0,x.grantee,x.grantor,x.privilege_type,x.is_grantable
          FROM pg_catalog.pg_database d CROSS JOIN principals p
          CROSS JOIN LATERAL aclexplode(COALESCE(d.datacl,acldefault('d',d.datdba))) x
          WHERE d.datname=current_database() AND (x.grantee=ANY(p.ids) OR x.grantee=0)
      )
      SELECT NOT EXISTS(SELECT * FROM actual EXCEPT ALL SELECT * FROM expected)
        AND NOT EXISTS(SELECT * FROM expected EXCEPT ALL SELECT * FROM actual)
        AND (SELECT datdba={creator} FROM pg_catalog.pg_database WHERE datname=current_database())
        AND (SELECT count(*) FROM pg_catalog.pg_roles WHERE oid IN ({owner},{authorizer},{executor})
          AND NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit
                   OR rolreplication OR rolbypassrls)
          AND rolcanlogin=(oid<>{owner}) AND rolconnlimit=-1 AND rolvaliduntil IS NULL)=3
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_auth_members CROSS JOIN principals p
          WHERE member=ANY(p.ids) OR roleid=ANY(p.ids))
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_default_acl)
        AND (SELECT count(*) FROM pg_catalog.pg_db_role_setting
          WHERE setrole IN ({authorizer},{executor})
          AND setdatabase=0 AND (SELECT array_agg(v ORDER BY v COLLATE "C")
            FROM unnest(setconfig) v)
            =ARRAY['TimeZone=UTC','lock_timeout=100ms',
                   'search_path=pg_catalog','statement_timeout=2000ms'])=2
        AND (SELECT count(*) FROM pg_catalog.pg_db_role_setting
          WHERE setrole IN ({owner},{authorizer},{executor}))=2
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_class c CROSS JOIN principals p
          WHERE c.relowner=ANY(p.ids) AND c.relpersistence<>'t'
            AND NOT (c.relowner={owner} AND c.oid IN (SELECT oid FROM control_relations)))
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_namespace n CROSS JOIN principals p
          WHERE n.nspowner=ANY(p.ids) AND n.oid NOT IN (SELECT oid FROM temporary)
            AND NOT (n.oid={cap_oid} AND n.nspowner={owner}))
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_proc f CROSS JOIN principals p
          WHERE f.proowner=ANY(p.ids) AND f.pronamespace NOT IN (SELECT oid FROM temporary)
            AND NOT (f.proowner={owner} AND f.oid IN ({functions})))
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type t CROSS JOIN principals p
          WHERE t.typowner=ANY(p.ids) AND t.typnamespace NOT IN (SELECT oid FROM temporary)
            AND NOT (t.typowner={owner} AND t.typnamespace={cap_oid}
              AND t.typname IN ('control','_control')));
      $body$;
      ALTER FUNCTION {cap}.principal_acl_ok() OWNER TO {owner_name};
      REVOKE ALL ON FUNCTION {cap}.principal_acl_ok() FROM PUBLIC;
    """).format(
        cap=sql.Identifier(namespace),
        owner=oid(owner),
        authorizer=oid(authorizer),
        executor=oid(executor),
        creator=oid(creator),
        owner_name=sql.Identifier("kasoma_eo_" + namespace.removeprefix("kasoma_cap_")),
        cap_oid=sql.SQL("{}::regnamespace::oid").format(sql.Literal(namespace)),
        crypto_oid=sql.SQL("{}::regnamespace::oid").format(sql.Literal(crypto)),
        expected=sql.SQL(",\n").join(expected),
        control=control,
        functions=sql.SQL(",").join(object_id("FUNCTION", namespace + "." + f) for f in FUNCTIONS),
    )
    return definition.as_string()


def fenced_scope_definition(base_ddl: str, namespace: str) -> str:
    """Amend only the checked source template, never a live function body."""
    header = (
        sql.SQL("CREATE FUNCTION {}.scope_identity_ok()")
        .format(sql.Identifier(namespace))
        .as_string()
    )
    if base_ddl.count(header) != 1:
        raise ValueError("Invalid closed scope recipe")
    start = base_ddl.index(header)
    end = base_ddl.index("\n$$;", start) + 4
    definition = base_ddl[start:end]
    return (
        definition[:-4].replace("CREATE FUNCTION", "CREATE OR REPLACE FUNCTION", 1)
        + sql.SQL(" AND {}.principal_acl_ok()\n$$;").format(sql.Identifier(namespace)).as_string()
    )
