-- ADR-073 metadata only, no application-row reads. Caller fixes search_path to pg_catalog.
WITH current_db AS MATERIALIZED (
  SELECT * FROM pg_catalog.pg_database WHERE datname=current_database()
), roles AS MATERIALIZED (
  SELECT r.oid,
    CASE WHEN r.oid=d.datdba THEN 'DATABASE_OWNER'
      WHEN r.rolname=:retirement_owner THEN 'EXPORT_RETIREMENT_OWNER'
      WHEN r.rolname='pg_database_owner' THEN 'DATABASE_OWNER_ROLE'
      ELSE 'ROLE:'||r.rolname END AS label,
    jsonb_build_array(r.rolsuper,r.rolinherit,r.rolcreaterole,r.rolcreatedb,
      r.rolcanlogin,r.rolreplication,r.rolbypassrls,r.rolconnlimit,r.rolvaliduntil) AS flags
  FROM pg_catalog.pg_roles r CROSS JOIN current_db d
), rels AS MATERIALIZED (
  SELECT c.*,n.nspname||'.'||c.relname AS qualified
  FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='public'
), funcs AS MATERIALIZED (
  SELECT p.*,p.oid::regprocedure::text AS signature FROM pg_catalog.pg_proc p
  JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public'
), types AS MATERIALIZED (
  SELECT t.*,n.nspname||'.'||t.typname AS qualified FROM pg_catalog.pg_type t
  JOIN pg_catalog.pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='public'
), acl_objects AS (
  SELECT 'RELATION:'||qualified AS name,relowner AS owner,
    COALESCE(relacl,acldefault(CASE WHEN relkind='S' THEN 'S' ELSE 'r' END::"char",relowner)) AS acl
  FROM rels WHERE relkind IN ('r','p','v','m','f','S')
  UNION ALL SELECT 'FUNCTION:'||signature,proowner,COALESCE(proacl,acldefault('f',proowner))
    FROM funcs
  UNION ALL SELECT 'TYPE:'||qualified,typowner,COALESCE(typacl,acldefault('T',typowner)) FROM types
  UNION ALL SELECT 'SCHEMA:'||nspname,nspowner,COALESCE(nspacl,acldefault('n',nspowner))
    FROM pg_catalog.pg_namespace WHERE nspname='public'
  UNION ALL SELECT 'DATABASE',datdba,COALESCE(datacl,acldefault('d',datdba)) FROM current_db
), objects(category,body) AS (
  SELECT 'roles',jsonb_build_array(label,flags) FROM roles
  UNION ALL SELECT 'memberships',jsonb_build_array(a.label,b.label,g.label,
    m.admin_option,m.inherit_option,m.set_option)
    FROM pg_catalog.pg_auth_members m JOIN roles a ON a.oid=m.roleid
    JOIN roles b ON b.oid=m.member JOIN roles g ON g.oid=m.grantor
  UNION ALL SELECT 'database',jsonb_build_array(d.encoding,d.datistemplate,d.datallowconn,
    d.datconnlimit,d.datlocprovider,d.datcollate,d.datctype,d.daticulocale,d.datcollversion,r.label)
    FROM current_db d JOIN roles r ON r.oid=d.datdba
  UNION ALL SELECT 'database_settings',jsonb_build_array(
    CASE WHEN s.setdatabase=0 THEN 'ALL' ELSE 'CURRENT' END,
    COALESCE(r.label,'ALL'),s.setconfig)
    FROM pg_catalog.pg_db_role_setting s LEFT JOIN roles r ON r.oid=s.setrole
    WHERE s.setdatabase=0 OR s.setdatabase=(SELECT oid FROM current_db)
  UNION ALL SELECT 'namespace',jsonb_build_array(n.nspname,r.label)
    FROM pg_catalog.pg_namespace n JOIN roles r ON r.oid=n.nspowner WHERE n.nspname='public'
  UNION ALL SELECT 'relations',jsonb_build_array(c.qualified,c.relkind,r.label,
    c.relpersistence,c.relrowsecurity,c.relforcerowsecurity,c.relreplident,c.relispartition,
    c.reloptions,a.amname,pg_get_expr(c.relpartbound,c.oid,true))
    FROM rels c JOIN roles r ON r.oid=c.relowner LEFT JOIN pg_catalog.pg_am a ON a.oid=c.relam
  UNION ALL SELECT 'attributes',jsonb_build_array(c.qualified,a.attnum,a.attname,
    a.atttypid::regtype::text,a.atttypmod,a.attndims,a.attnotnull,a.attidentity,a.attgenerated,
    a.attisdropped,a.attstorage,a.attcompression,a.attinhcount,a.attislocal,
    n.nspname||'.'||k.collname,pg_get_expr(d.adbin,d.adrelid,true))
    FROM rels c JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid AND a.attnum>0
    LEFT JOIN pg_catalog.pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
    LEFT JOIN pg_catalog.pg_collation k ON k.oid=a.attcollation
    LEFT JOIN pg_catalog.pg_namespace n ON n.oid=k.collnamespace
  UNION ALL SELECT 'constraints',jsonb_build_array(COALESCE(r.qualified,t.qualified),c.conname,
    c.contype,c.condeferrable,c.condeferred,c.convalidated,c.conislocal,c.coninhcount,
    c.connoinherit,pg_get_constraintdef(c.oid,true))
    FROM pg_catalog.pg_constraint c LEFT JOIN rels r ON r.oid=c.conrelid
    LEFT JOIN types t ON t.oid=c.contypid WHERE r.oid IS NOT NULL OR t.oid IS NOT NULL
  UNION ALL SELECT 'indexes',jsonb_build_array(c.qualified,i.indnatts,i.indnkeyatts,i.indisunique,
    i.indnullsnotdistinct,i.indisprimary,i.indisexclusion,i.indimmediate,i.indisclustered,
    i.indisvalid,i.indcheckxmin,i.indisready,i.indislive,i.indisreplident,
    pg_get_indexdef(i.indexrelid))
    FROM pg_catalog.pg_index i JOIN rels c ON c.oid=i.indexrelid
  UNION ALL SELECT 'triggers',jsonb_build_array(r.qualified,
    CASE WHEN t.tgisinternal THEN 'INTERNAL' ELSE t.tgname END,
    t.tgfoid::regprocedure::text,t.tgtype,t.tgenabled,t.tgisinternal,
    t.tgdeferrable,t.tginitdeferred,t.tgnargs,t.tgattr::text,encode(t.tgargs,'hex'),
    t.tgoldtable,t.tgnewtable,pg_get_expr(t.tgqual,t.tgrelid,true),c.conname,
    c.conrelid::regclass::text,c.confrelid::regclass::text)
    FROM pg_catalog.pg_trigger t JOIN rels r ON r.oid=t.tgrelid
    LEFT JOIN pg_catalog.pg_constraint c ON c.oid=t.tgconstraint
  UNION ALL SELECT 'functions',jsonb_build_array(p.signature,r.label,l.lanname,p.prokind,
    p.prosecdef,p.proisstrict,p.proleakproof,p.provolatile,p.proparallel,
    p.procost,p.prorows,p.prosupport::regprocedure::text,
    pg_get_function_arguments(p.oid),pg_get_function_result(p.oid),
    __DYNAMIC_BODY__,p.probin,p.proconfig)
    FROM funcs p JOIN roles r ON r.oid=p.proowner JOIN pg_catalog.pg_language l ON l.oid=p.prolang
  UNION ALL SELECT 'aggregates',jsonb_build_array(p.signature,a.aggkind,a.aggnumdirectargs,
    a.aggtransfn::regprocedure::text,a.aggfinalfn::regprocedure::text,
    a.aggcombinefn::regprocedure::text,a.aggserialfn::regprocedure::text,
    a.aggdeserialfn::regprocedure::text,a.aggmtransfn::regprocedure::text,
    a.aggminvtransfn::regprocedure::text,a.aggmfinalfn::regprocedure::text,
    a.aggfinalextra,a.aggmfinalextra,a.aggfinalmodify,a.aggmfinalmodify,
    a.aggsortop::regoperator::text,a.aggtranstype::regtype::text,a.aggtransspace,
    a.aggmtranstype::regtype::text,a.aggmtransspace,a.agginitval,a.aggminitval)
    FROM pg_catalog.pg_aggregate a JOIN funcs p ON p.oid=a.aggfnoid
  UNION ALL SELECT 'types',jsonb_build_array(t.qualified,r.label,t.typlen,t.typbyval,
    t.typtype,t.typcategory,t.typispreferred,t.typisdefined,t.typdelim,t.typalign,
    t.typstorage,t.typnotnull,t.typtypmod,t.typndims,t.typdefault,
    t.typelem::regtype::text,t.typbasetype::regtype::text,
    t.typinput::regprocedure::text,t.typoutput::regprocedure::text,
    t.typreceive::regprocedure::text,t.typsend::regprocedure::text,
    t.typmodin::regprocedure::text,t.typmodout::regprocedure::text,t.typanalyze::regprocedure::text)
    FROM types t JOIN roles r ON r.oid=t.typowner
  UNION ALL SELECT 'enums',jsonb_build_array(t.qualified,e.enumsortorder,e.enumlabel)
    FROM pg_catalog.pg_enum e JOIN types t ON t.oid=e.enumtypid
  UNION ALL SELECT 'acl',jsonb_build_array(a.name,owner.label,
    COALESCE(g.label,'PUBLIC'),grantor.label,x.privilege_type,x.is_grantable)
    FROM acl_objects a CROSS JOIN LATERAL aclexplode(a.acl) x
    JOIN roles owner ON owner.oid=a.owner JOIN roles grantor ON grantor.oid=x.grantor
    LEFT JOIN roles g ON g.oid=x.grantee
  UNION ALL SELECT 'attribute_acl',jsonb_build_array(c.qualified,a.attname,
    COALESCE(g.label,'PUBLIC'),grantor.label,x.privilege_type,x.is_grantable)
    FROM rels c JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid AND a.attnum>0
    CROSS JOIN LATERAL aclexplode(a.attacl) x JOIN roles grantor ON grantor.oid=x.grantor
    LEFT JOIN roles g ON g.oid=x.grantee
  UNION ALL SELECT 'default_acl',jsonb_build_array(owner.label,COALESCE(n.nspname,'GLOBAL'),
    d.defaclobjtype,COALESCE(g.label,'PUBLIC'),grantor.label,x.privilege_type,x.is_grantable)
    FROM pg_catalog.pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) x
    JOIN roles owner ON owner.oid=d.defaclrole JOIN roles grantor ON grantor.oid=x.grantor
    LEFT JOIN roles g ON g.oid=x.grantee LEFT JOIN pg_catalog.pg_namespace n ON n.oid=d.defaclnamespace
  UNION ALL SELECT 'policies',jsonb_build_array(r.qualified,p.polname,p.polcmd,p.polpermissive,
    (SELECT jsonb_agg(COALESCE(x.label,'PUBLIC') ORDER BY COALESCE(x.label,'PUBLIC'))
      FROM unnest(p.polroles) v LEFT JOIN roles x ON x.oid=v),
    pg_get_expr(p.polqual,p.polrelid,true),pg_get_expr(p.polwithcheck,p.polrelid,true))
    FROM pg_catalog.pg_policy p JOIN rels r ON r.oid=p.polrelid
  UNION ALL SELECT 'rules',jsonb_build_array(r.qualified,w.rulename,w.ev_type,w.ev_enabled,
    w.is_instead,pg_get_ruledef(w.oid,true)) FROM pg_catalog.pg_rewrite w JOIN rels r ON r.oid=w.ev_class
  UNION ALL SELECT 'extensions',jsonb_build_array(e.extname,n.nspname,r.label,
    e.extversion,e.extrelocatable)
    FROM pg_catalog.pg_extension e JOIN pg_catalog.pg_namespace n ON n.oid=e.extnamespace
    JOIN roles r ON r.oid=e.extowner
  UNION ALL SELECT 'operators',jsonb_build_array(o.oid::regoperator::text,r.label,o.oprkind,
    o.oprcanmerge,o.oprcanhash,o.oprresult::regtype::text,o.oprcom::regoperator::text,
    o.oprnegate::regoperator::text,o.oprcode::regprocedure::text,
    o.oprrest::regprocedure::text,o.oprjoin::regprocedure::text)
    FROM pg_catalog.pg_operator o JOIN pg_catalog.pg_namespace n ON n.oid=o.oprnamespace
    JOIN roles r ON r.oid=o.oprowner WHERE n.nspname='public'
  UNION ALL SELECT 'casts',jsonb_build_array(c.castsource::regtype::text,c.casttarget::regtype::text,
    c.castfunc::regprocedure::text,c.castcontext,c.castmethod)
    FROM pg_catalog.pg_cast c WHERE c.castsource IN(SELECT oid FROM types)
      OR c.casttarget IN(SELECT oid FROM types)
  UNION ALL SELECT 'opclasses',jsonb_build_array(n.nspname||'.'||c.opcname,r.label,a.amname,
    f.opfnamespace::regnamespace::text||'.'||f.opfname,c.opcintype::regtype::text,c.opckeytype::regtype::text,c.opcdefault)
    FROM pg_catalog.pg_opclass c JOIN pg_catalog.pg_namespace n ON n.oid=c.opcnamespace
    JOIN roles r ON r.oid=c.opcowner JOIN pg_catalog.pg_am a ON a.oid=c.opcmethod
    JOIN pg_catalog.pg_opfamily f ON f.oid=c.opcfamily WHERE n.nspname='public'
  UNION ALL SELECT 'opfamilies',jsonb_build_array(n.nspname||'.'||f.opfname,r.label,a.amname)
    FROM pg_catalog.pg_opfamily f JOIN pg_catalog.pg_namespace n ON n.oid=f.opfnamespace
    JOIN roles r ON r.oid=f.opfowner JOIN pg_catalog.pg_am a ON a.oid=f.opfmethod
    WHERE n.nspname='public'
  UNION ALL SELECT 'amop',jsonb_build_array(n.nspname||'.'||f.opfname,o.amopstrategy,
    o.amoplefttype::regtype::text,o.amoprighttype::regtype::text,o.amoppurpose,
    o.amopopr::regoperator::text,s.opfnamespace::regnamespace::text||'.'||s.opfname)
    FROM pg_catalog.pg_amop o JOIN pg_catalog.pg_opfamily f ON f.oid=o.amopfamily
    JOIN pg_catalog.pg_namespace n ON n.oid=f.opfnamespace
    LEFT JOIN pg_catalog.pg_opfamily s ON s.oid=o.amopsortfamily WHERE n.nspname='public'
  UNION ALL SELECT 'amproc',jsonb_build_array(n.nspname||'.'||f.opfname,p.amprocnum,
    p.amproclefttype::regtype::text,p.amprocrighttype::regtype::text,p.amproc::regprocedure::text)
    FROM pg_catalog.pg_amproc p JOIN pg_catalog.pg_opfamily f ON f.oid=p.amprocfamily
    JOIN pg_catalog.pg_namespace n ON n.oid=f.opfnamespace WHERE n.nspname='public'
  UNION ALL SELECT 'inheritance',jsonb_build_array(i.inhrelid::regclass::text,
    i.inhparent::regclass::text,i.inhseqno,i.inhdetachpending)
    FROM pg_catalog.pg_inherits i WHERE i.inhrelid IN(SELECT oid FROM rels)
      OR i.inhparent IN(SELECT oid FROM rels)
  UNION ALL SELECT 'collations',to_jsonb(c)-ARRAY['oid','collnamespace','collowner']
    FROM pg_catalog.pg_collation c JOIN pg_catalog.pg_namespace n ON n.oid=c.collnamespace
    WHERE n.nspname='public'
  UNION ALL SELECT 'conversions',jsonb_build_array(c.conname,r.label,c.conforencoding,
    c.contoencoding,c.conproc::regprocedure::text,c.condefault)
    FROM pg_catalog.pg_conversion c JOIN pg_catalog.pg_namespace n ON n.oid=c.connamespace
    JOIN roles r ON r.oid=c.conowner WHERE n.nspname='public'
  UNION ALL SELECT 'event_triggers',jsonb_build_array(e.evtname,e.evtevent,r.label,
    e.evtfoid::regprocedure::text,e.evtenabled,e.evttags)
    FROM pg_catalog.pg_event_trigger e JOIN roles r ON r.oid=e.evtowner
  UNION ALL SELECT 'foreign_controls',jsonb_build_array('WRAPPER',f.fdwname,r.label,
    f.fdwhandler::regprocedure::text,f.fdwvalidator::regprocedure::text,f.fdwoptions)
    FROM pg_catalog.pg_foreign_data_wrapper f JOIN roles r ON r.oid=f.fdwowner
  UNION ALL SELECT 'foreign_controls',jsonb_build_array('SERVER',s.srvname,r.label,
    s.srvtype,s.srvversion,s.srvoptions) FROM pg_catalog.pg_foreign_server s
    JOIN roles r ON r.oid=s.srvowner
  UNION ALL SELECT 'text_search',jsonb_build_array('CONFIG',c.cfgname,r.label,
    c.cfgparser::regproc::text) FROM pg_catalog.pg_ts_config c
    JOIN pg_catalog.pg_namespace n ON n.oid=c.cfgnamespace JOIN roles r ON r.oid=c.cfgowner
    WHERE n.nspname='public'
  UNION ALL SELECT 'text_search',jsonb_build_array('DICTIONARY',d.dictname,r.label,
    d.dicttemplate::text,d.dictinitoption) FROM pg_catalog.pg_ts_dict d
    JOIN pg_catalog.pg_namespace n ON n.oid=d.dictnamespace JOIN roles r ON r.oid=d.dictowner
    WHERE n.nspname='public'
  UNION ALL SELECT 'text_search',jsonb_build_array('PARSER',p.prsname)
    FROM pg_catalog.pg_ts_parser p JOIN pg_catalog.pg_namespace n ON n.oid=p.prsnamespace
    WHERE n.nspname='public'
  UNION ALL SELECT 'text_search',jsonb_build_array('TEMPLATE',t.tmplname)
    FROM pg_catalog.pg_ts_template t JOIN pg_catalog.pg_namespace n ON n.oid=t.tmplnamespace
    WHERE n.nspname='public'
), categories(category) AS (VALUES
  ('roles'),('memberships'),('database'),('database_settings'),('namespace'),('relations'),
  ('attributes'),('constraints'),('indexes'),('triggers'),('functions'),('aggregates'),('types'),('enums'),
  ('acl'),('attribute_acl'),('default_acl'),('policies'),('rules'),('extensions'),('operators'),
  ('casts'),('opclasses'),('opfamilies'),('amop'),('amproc'),('inheritance'),('collations'),
  ('conversions'),('event_triggers'),('foreign_controls'),('text_search')
)
SELECT c.category,count(o.body)::integer AS count,
  encode(sha256(convert_to(COALESCE(jsonb_agg(o.body ORDER BY o.body::text)
    FILTER(WHERE o.body IS NOT NULL),'[]'::jsonb)::text,'UTF8')),'hex') AS digest
FROM categories c LEFT JOIN objects o ON o.category=c.category
GROUP BY c.category ORDER BY c.category
