-- ADR-076 unsigned Datum codec compiled into raw pg_node_tree fields;
-- ADR-073 raw safety stage: no pg_get_expr/definition deparser or user I/O invocation.
, raw_objects(category,body) AS (
  SELECT 'functions',jsonb_build_array(p.signature,r.label,l.lanname,p.prokind,
    p.prosecdef,p.proisstrict,p.proleakproof,p.provolatile,p.proparallel,p.procost,p.prorows,
    p.prosupport::regprocedure::text,p.proargnames,p.proargmodes,p.pronargdefaults,
    ARRAY(SELECT x::regtype::text FROM unnest(p.proargtypes) x),
    CASE WHEN p.proallargtypes IS NULL THEN NULL ELSE
      ARRAY(SELECT x::regtype::text FROM unnest(p.proallargtypes) x) END,
    p.prorettype::regtype::text,__NODE_ARG_DEFAULTS__,__DYNAMIC_BODY__,p.probin,p.proconfig)
    FROM funcs p JOIN roles r ON r.oid=p.proowner JOIN pg_catalog.pg_language l ON l.oid=p.prolang
  UNION ALL SELECT 'types',jsonb_build_array(t.qualified,r.label,t.typlen,t.typbyval,
    t.typtype,t.typcategory,t.typispreferred,t.typisdefined,t.typdelim,t.typalign,
    t.typstorage,t.typnotnull,t.typtypmod,t.typndims,t.typdefault,__NODE_TYPE_DEFAULT__,
    t.typelem::regtype::text,t.typbasetype::regtype::text,t.typrelid::regclass::text,
    t.typinput::regprocedure::text,t.typoutput::regprocedure::text,
    t.typreceive::regprocedure::text,t.typsend::regprocedure::text,
    t.typmodin::regprocedure::text,t.typmodout::regprocedure::text,t.typanalyze::regprocedure::text)
    FROM types t JOIN roles r ON r.oid=t.typowner
  UNION ALL SELECT 'defaults',jsonb_build_array(c.qualified,a.attname,__NODE_COLUMN_DEFAULT__)
    FROM rels c JOIN pg_catalog.pg_attrdef d ON d.adrelid=c.oid
    JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid AND a.attnum=d.adnum
  UNION ALL SELECT 'constraints',jsonb_build_array(COALESCE(r.qualified,t.qualified),c.conname,
    c.contype,__NODE_CONSTRAINT__,c.conkey,c.confkey,c.condeferrable,c.condeferred,c.convalidated,
    c.confupdtype,c.confdeltype,c.confmatchtype,c.conislocal,c.coninhcount,c.connoinherit)
    FROM pg_catalog.pg_constraint c LEFT JOIN rels r ON r.oid=c.conrelid
    LEFT JOIN types t ON t.oid=c.contypid WHERE r.oid IS NOT NULL OR t.oid IS NOT NULL
  UNION ALL SELECT 'indexes',jsonb_build_array(c.qualified,i.indnatts,i.indnkeyatts,i.indisunique,
    i.indnullsnotdistinct,i.indisprimary,i.indisexclusion,i.indimmediate,i.indisvalid,
    i.indisready,i.indislive,i.indkey::text,i.indclass::text,i.indoption::text,
    __NODE_INDEX_EXPRESSION__,__NODE_INDEX_PREDICATE__)
    FROM pg_catalog.pg_index i JOIN rels c ON c.oid=i.indexrelid
  UNION ALL SELECT 'triggers',jsonb_build_array(r.qualified,
    CASE WHEN t.tgisinternal THEN 'INTERNAL' ELSE t.tgname END,
    t.tgfoid::regprocedure::text,t.tgtype,t.tgenabled,t.tgisinternal,
    t.tgdeferrable,t.tginitdeferred,t.tgnargs,t.tgattr::text,encode(t.tgargs,'hex'),
    t.tgoldtable,t.tgnewtable,__NODE_TRIGGER__,c.conname,
    c.conrelid::regclass::text,c.confrelid::regclass::text)
    FROM pg_catalog.pg_trigger t JOIN rels r ON r.oid=t.tgrelid
    LEFT JOIN pg_catalog.pg_constraint c ON c.oid=t.tgconstraint
  UNION ALL SELECT 'policies',jsonb_build_array(r.qualified,p.polname,p.polcmd,p.polpermissive,
    __NODE_POLICY_QUAL__,__NODE_POLICY_CHECK__)
    FROM pg_catalog.pg_policy p JOIN rels r ON r.oid=p.polrelid
  UNION ALL SELECT 'rules',jsonb_build_array(r.qualified,w.rulename,w.ev_type,w.ev_enabled,
    w.is_instead,__NODE_RULE_QUAL__,__NODE_RULE_ACTION__)
    FROM pg_catalog.pg_rewrite w JOIN rels r ON r.oid=w.ev_class
  UNION ALL SELECT 'relations',jsonb_build_array(c.qualified,c.relkind,c.relispartition,
    __NODE_PARTITION__) FROM rels c
), raw_categories(category) AS (VALUES ('functions'),('types'),('defaults'),('constraints'),
  ('indexes'),('triggers'),('policies'),('rules'),('relations'))
SELECT c.category,count(o.body)::integer AS count,
  encode(sha256(convert_to(COALESCE(jsonb_agg(o.body ORDER BY o.body::text)
    FILTER(WHERE o.body IS NOT NULL),'[]'::jsonb)::text,'UTF8')),'hex') AS digest
FROM raw_categories c LEFT JOIN raw_objects o ON o.category=c.category
GROUP BY c.category ORDER BY c.category
