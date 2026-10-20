-- ADR-071 forward capability installation in an exclusively created source only.
-- Ordinary Alembic migrations/startup never read or execute this template.
REVOKE ALL ON SCHEMA __CAP__,__CRYPTO__ FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA __CRYPTO__ FROM PUBLIC;
GRANT USAGE ON SCHEMA __CRYPTO__ TO __OWNER__;
GRANT EXECUTE ON FUNCTION __CRYPTO__.hmac(bytea,bytea,text) TO __OWNER__;
GRANT USAGE ON SCHEMA public TO __OWNER__;
GRANT SELECT ON public.account_erasure_state,public.account_erasure_jobs,
  public.account_erasure_plans TO __OWNER__;
GRANT UPDATE ON public.account_erasure_state TO __OWNER__;

CREATE TABLE __CAP__.control (
  singleton integer PRIMARY KEY CHECK (singleton=1),
  database_oid oid NOT NULL CHECK (database_oid=__DATABASE_OID__),
  namespace_oid oid NOT NULL CHECK (namespace_oid=__NAMESPACE_OID__),
  cap_namespace_oid oid NOT NULL DEFAULT pg_catalog.to_regnamespace('__CAP__')::oid,
  crypto_namespace_oid oid NOT NULL DEFAULT pg_catalog.to_regnamespace('__CRYPTO__')::oid,
  crypto_hmac_oid oid NOT NULL DEFAULT
    pg_catalog.to_regprocedure('__CRYPTO__.hmac(bytea,bytea,text)')::oid,
  source_nonce uuid NOT NULL,
  installation_nonce uuid NOT NULL CHECK (installation_nonce='__INSTALLATION_NONCE__'::uuid),
  owner_oid oid NOT NULL CHECK (owner_oid=__OWNER_OID__),
  authorizer_oid oid NOT NULL CHECK (authorizer_oid=__AUTHORIZER_OID__),
  executor_oid oid NOT NULL CHECK (executor_oid=__EXECUTOR_OID__),
  version text NOT NULL CHECK (version='isolated-erasure-capability-v1'),
  fingerprint_key bytea NOT NULL CHECK (octet_length(fingerprint_key)=32),
  creation_enabled boolean NOT NULL DEFAULT false CHECK (NOT creation_enabled),
  execution_enabled boolean NOT NULL DEFAULT false CHECK (NOT execution_enabled),
  installed_at timestamptz NOT NULL DEFAULT clock_timestamp()
    CHECK (isfinite(installed_at))
);
ALTER TABLE __CAP__.control OWNER TO __OWNER__;
REVOKE ALL ON __CAP__.control FROM PUBLIC;

CREATE FUNCTION __CAP__.control_guard() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
  IF TG_OP='INSERT' AND current_user::regrole::oid=__OWNER_OID__ THEN
    IF NOT EXISTS(SELECT 1 FROM __CAP__.control) THEN RETURN NEW; END IF;
  END IF;
  RAISE EXCEPTION 'Erasure bootstrap control is immutable' USING ERRCODE='42501';
END $$;
ALTER FUNCTION __CAP__.control_guard() OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.control_guard() FROM PUBLIC;
CREATE TRIGGER immutable_erasure_control BEFORE INSERT OR UPDATE OR DELETE
  ON __CAP__.control FOR EACH ROW EXECUTE FUNCTION __CAP__.control_guard();
CREATE TRIGGER no_truncate_erasure_control BEFORE TRUNCATE ON __CAP__.control
  FOR EACH STATEMENT EXECUTE FUNCTION __CAP__.control_guard();

CREATE FUNCTION __CAP__.initialize_control(key bytea) RETURNS void
LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
  IF current_user::regrole::oid<>__OWNER_OID__ THEN
    RAISE EXCEPTION 'Erasure control initialization unavailable' USING ERRCODE='42501';
  END IF;
  BEGIN
    INSERT INTO __CAP__.control(singleton,database_oid,namespace_oid,source_nonce,
      installation_nonce,owner_oid,authorizer_oid,executor_oid,version,fingerprint_key)
    SELECT 1,__DATABASE_OID__,__NAMESPACE_OID__,a.scope_nonce,
      '__INSTALLATION_NONCE__'::uuid,__OWNER_OID__,__AUTHORIZER_OID__,__EXECUTOR_OID__,
      'isolated-erasure-capability-v1',key
    FROM public.account_erasure_state a WHERE a.singleton=1
      AND a.database_oid=__DATABASE_OID__ AND a.namespace_oid=__NAMESPACE_OID__
      AND NOT a.original_scope_eligible AND a.owner_oid IS NULL AND a.executor_oid IS NULL
      AND NOT a.creation_enabled AND NOT a.execution_enabled;
    IF NOT FOUND THEN RAISE EXCEPTION 'Erasure source unavailable'; END IF;
  EXCEPTION WHEN OTHERS THEN
    -- Do not expose a rejected row/key through PostgreSQL's uncaught CHECK detail.
    RAISE EXCEPTION 'Erasure control initialization unavailable' USING ERRCODE='42501';
  END;
END $$;
ALTER FUNCTION __CAP__.initialize_control(bytea) OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.initialize_control(bytea) FROM PUBLIC;

CREATE FUNCTION __CAP__.scope_identity_ok() RETURNS boolean
LANGUAGE sql STABLE SET search_path=pg_catalog AS $$
  SELECT current_user::regrole::oid=__OWNER_OID__ AND EXISTS(
    SELECT 1 FROM __CAP__.control c
    JOIN pg_catalog.pg_database d ON d.oid=c.database_oid AND d.datname=current_database()
    JOIN pg_catalog.pg_namespace s ON s.oid=c.namespace_oid AND s.nspname='public'
    JOIN pg_catalog.pg_namespace n ON n.oid=c.cap_namespace_oid AND n.nspowner=c.owner_oid
      AND n.oid=pg_catalog.to_regnamespace('__CAP__')
    JOIN pg_catalog.pg_namespace q ON q.oid=c.crypto_namespace_oid
      AND q.oid=pg_catalog.to_regnamespace('__CRYPTO__')
    JOIN pg_catalog.pg_extension e ON e.extnamespace=q.oid AND e.extname='pgcrypto'
      AND e.extversion='1.3' AND e.extowner=d.datdba
    JOIN pg_catalog.pg_proc p ON p.oid=c.crypto_hmac_oid AND p.pronamespace=q.oid
      AND p.proname='hmac' AND NOT p.prosecdef
      AND p.oid=pg_catalog.to_regprocedure('__CRYPTO__.hmac(bytea,bytea,text)')
    JOIN public.account_erasure_state a ON a.singleton=1
      AND a.database_oid=c.database_oid AND a.namespace_oid=c.namespace_oid
      AND a.scope_nonce=c.source_nonce AND a.policy='synthetic-account-erasure-v1'
      AND a.manifest='erasure-0045-v1'
    WHERE c.singleton=1 AND c.database_oid=__DATABASE_OID__
      AND c.namespace_oid=__NAMESPACE_OID__ AND c.owner_oid=__OWNER_OID__
      AND c.authorizer_oid=__AUTHORIZER_OID__ AND c.executor_oid=__EXECUTOR_OID__
      AND c.version='isolated-erasure-capability-v1'
      AND (SELECT count(*) FROM pg_catalog.pg_roles r
        WHERE r.oid IN (c.owner_oid,c.authorizer_oid,c.executor_oid)
          AND NOT (r.rolsuper OR r.rolcreatedb OR r.rolcreaterole OR r.rolinherit
                   OR r.rolreplication OR r.rolbypassrls)
          AND r.rolcanlogin=(r.oid<>c.owner_oid))=3
      AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_auth_members m
        WHERE m.member IN (c.owner_oid,c.authorizer_oid,c.executor_oid)
           OR m.roleid IN (c.owner_oid,c.authorizer_oid,c.executor_oid))
  )
$$;
ALTER FUNCTION __CAP__.scope_identity_ok() OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.scope_identity_ok() FROM PUBLIC;

-- Replace the dormant guard with its explicitly installed forward bootstrap peer.
-- Only a single owner/OID/nonce-bound metadata handoff is possible. Plan/job DML,
-- activation and closed_at remain forbidden, including for the SQL owner itself.
CREATE OR REPLACE FUNCTION public.account_erasure_dormant_guard() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
  IF TG_OP<>'UPDATE' OR TG_TABLE_NAME<>'account_erasure_state'
      OR current_user::regrole::oid<>__OWNER_OID__ THEN
    RAISE EXCEPTION 'Erasure execution capability is not installed' USING ERRCODE='42501';
  END IF;
  IF NOT __CAP__.scope_identity_ok() OR OLD.original_scope_eligible
      OR NOT NEW.original_scope_eligible OR NEW.owner_oid IS DISTINCT FROM __OWNER_OID__
      OR NEW.executor_oid IS DISTINCT FROM __EXECUTOR_OID__
      OR (to_jsonb(NEW)-ARRAY['original_scope_eligible','owner_oid','executor_oid'])
        IS DISTINCT FROM
         (to_jsonb(OLD)-ARRAY['original_scope_eligible','owner_oid','executor_oid']) THEN
    RAISE EXCEPTION 'Erasure bootstrap state is immutable' USING ERRCODE='42501';
  END IF;
  RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION public.account_erasure_dormant_guard() FROM PUBLIC;
ALTER TABLE public.account_erasure_state
  DROP CONSTRAINT account_erasure_state_original_scope_eligible_check,
  DROP CONSTRAINT account_erasure_state_owner_oid_check,
  DROP CONSTRAINT account_erasure_state_executor_oid_check;
ALTER TABLE public.account_erasure_state ADD CONSTRAINT account_erasure_state_bound_owner
  CHECK ((NOT original_scope_eligible AND owner_oid IS NULL AND executor_oid IS NULL)
    OR (original_scope_eligible AND owner_oid IS NOT NULL AND executor_oid IS NOT NULL
        AND owner_oid=__OWNER_OID__ AND executor_oid=__EXECUTOR_OID__));

CREATE FUNCTION __CAP__.readiness() RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
BEGIN
  IF session_user::regrole::oid NOT IN (__AUTHORIZER_OID__,__EXECUTOR_OID__)
      OR NOT __CAP__.scope_identity_ok() THEN
    RAISE EXCEPTION 'Erasure capability unavailable' USING ERRCODE='42501';
  END IF;
  IF NOT EXISTS(SELECT 1 FROM public.account_erasure_state
    WHERE singleton=1 AND original_scope_eligible AND owner_oid=__OWNER_OID__
      AND executor_oid=__EXECUTOR_OID__ AND NOT creation_enabled AND NOT execution_enabled) THEN
    RAISE EXCEPTION 'Erasure capability unavailable' USING ERRCODE='42501';
  END IF;
  RETURN jsonb_build_object('version','isolated-erasure-capability-v1',
    'creation_enabled',false,'execution_enabled',false);
END $$;
ALTER FUNCTION __CAP__.readiness() OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.readiness() FROM PUBLIC;
GRANT USAGE ON SCHEMA __CAP__ TO __AUTHORIZER__,__EXECUTOR__;
GRANT EXECUTE ON FUNCTION __CAP__.readiness() TO __AUTHORIZER__,__EXECUTOR__;
