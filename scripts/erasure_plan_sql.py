"""ADR-072 trusted installer compiler: closed manifest/predicates, never request SQL."""

import json

from psycopg import sql

from services.erasure_manifest import BASELINE, BASELINE_REVISION
from services.erasure_sources import PREDICATES, assert_registry


def compile_plan_helpers(namespace: str, crypto: str) -> str:
    assert_registry()
    expected = {
        name: {
            "kind": "r",
            "key": list(source.primary_key),
            "cols": [[c.name, c.type_name, c.nullable] for c in source.columns],
        }
        for name, source in BASELINE.items()
    }
    shape = sql.SQL("""
      CREATE FUNCTION {cap}.source_shape_ok() RETURNS boolean LANGUAGE sql STABLE
      SET search_path=pg_catalog SET timezone='UTC' AS $body$
        WITH sources AS (
          SELECT c.oid,c.relname,c.relkind FROM pg_catalog.pg_class c
          WHERE c.relnamespace=pg_catalog.to_regnamespace('public')
            AND c.relkind IN ('r','p','v','m','f')
        ), observed AS (
          SELECT jsonb_object_agg(s.relname,jsonb_build_object(
            'kind',s.relkind,'key',
            (SELECT array_agg(a.attname::text ORDER BY k.ordinality)
             FROM pg_catalog.pg_constraint p
             CROSS JOIN LATERAL unnest(p.conkey) WITH ORDINALITY k(attnum,ordinality)
             JOIN pg_catalog.pg_attribute a ON a.attrelid=p.conrelid AND a.attnum=k.attnum
             WHERE p.conrelid=s.oid AND p.contype='p'),
            'cols',(SELECT jsonb_agg(jsonb_build_array(a.attname,
              CASE WHEN t.typnamespace='pg_catalog'::regnamespace THEN t.typname::text
                ELSE 'UNSUPPORTED_TYPE' END,NOT a.attnotnull) ORDER BY a.attnum)
              FROM pg_catalog.pg_attribute a JOIN pg_catalog.pg_type t ON t.oid=a.atttypid
              WHERE a.attrelid=s.oid AND a.attnum>0 AND NOT a.attisdropped)
          )) AS shape FROM sources s
        ) SELECT shape={expected}::jsonb AND
          (SELECT array_agg(version_num::text ORDER BY version_num)
            FROM public.alembic_version)=ARRAY[{revision}]::text[] FROM observed;
      $body$;
    """).format(
        cap=sql.Identifier(namespace),
        expected=sql.Literal(json.dumps(expected)),
        revision=sql.Literal(BASELINE_REVISION),
    )
    blocks = []
    for name in sorted(PREDICATES):
        source = BASELINE[name]
        predicate = PREDICATES[name]
        query: sql.Composable = sql.SQL("")
        if predicate is not None:
            body = sql.SQL("to_jsonb(x)")
            if name == "account_erasure_plans":
                body = sql.SQL(
                    "CASE WHEN x.id=_plan THEN to_jsonb(x)-'version' ELSE to_jsonb(x) END"
                )
            query = sql.SQL("""
              FOR _row IN SELECT sha256(convert_to(x.xmin::text || ':' || ({body})::text,
                'UTF8')) AS digest FROM public.{table} x WHERE {predicate} ORDER BY {order}
              LOOP
                _state:={crypto}.hmac(convert_to('R','UTF8')||_state||_row.digest,_key,'sha256');
                _count:=_count+1;
              END LOOP;
            """).format(
                body=body,
                table=sql.Identifier(name),
                predicate=sql.SQL(
                    predicate.replace("__S__", "public").replace(":subject", "_subject")
                ),
                order=sql.SQL(",").join(
                    sql.SQL("x.{}").format(sql.Identifier(k)) for k in source.primary_key
                ),
                crypto=sql.Identifier(crypto),
            )
        blocks.append(
            sql.SQL("""
          _state:={crypto}.hmac(convert_to('S','UTF8')||_state||int4send(octet_length({name}))
            ||convert_to({name},'UTF8'),_key,'sha256');
          _count:=0;
          {query}
          _state:={crypto}.hmac(convert_to('E','UTF8')||_state||int8send(_count),_key,'sha256');
        """).format(crypto=sql.Identifier(crypto), name=sql.Literal(name), query=query)
        )
    seal = sql.SQL("""
      CREATE FUNCTION {cap}.source_version(_subject uuid,_plan uuid) RETURNS text
      LANGUAGE plpgsql SET search_path=pg_catalog SET timezone='UTC' AS $body$
      DECLARE _key bytea; _state bytea; _row record; _count bigint;
      BEGIN
        IF NOT {cap}.scope_identity_ok() OR NOT {cap}.source_shape_ok() THEN
          RAISE EXCEPTION 'Erasure source unavailable' USING ERRCODE='42501';
        END IF;
        SELECT fingerprint_key,{crypto}.hmac(convert_to(
          'kasoma.erasure.source.v2:'||database_oid::text||':'||namespace_oid::text||':'||
          source_nonce::text||':'||installation_nonce::text||':'||_subject::text||':'||
          _plan::text||':'||'erasure-0045-v1','UTF8'),fingerprint_key,'sha256')
        INTO _key,_state FROM {cap}.control WHERE singleton=1;
        {blocks}
        RETURN encode(_state,'hex');
      END $body$;
    """).format(
        cap=sql.Identifier(namespace),
        crypto=sql.Identifier(crypto),
        blocks=sql.SQL("\n").join(blocks),
    )
    return (shape + seal).as_string()
