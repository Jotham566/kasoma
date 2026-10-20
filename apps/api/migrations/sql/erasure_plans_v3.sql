-- ADR-070/072 private plan gate, fresh v3 recipe only. No job/closure capability.
GRANT SELECT ON ALL TABLES IN SCHEMA public TO __OWNER__;
GRANT INSERT,UPDATE,DELETE ON public.account_erasure_plans TO __OWNER__;
GRANT INSERT ON public.audit_log TO __OWNER__;
-- PostgreSQL row locks require UPDATE on at least one column. These owner-only
-- ID grants support FOR SHARE, not a new callable source-mutation operation.
GRANT UPDATE(id) ON public.auth_sessions,public.users,public.data_subject_requests TO __OWNER__;
GRANT UPDATE(user_id) ON public.user_roles TO __OWNER__;
GRANT UPDATE(request_id) ON public.data_request_reviews TO __OWNER__;
ALTER FUNCTION __CAP__.source_shape_ok() OWNER TO __OWNER__;
ALTER FUNCTION __CAP__.source_version(uuid,uuid) OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.source_shape_ok(),__CAP__.source_version(uuid,uuid) FROM PUBLIC;

CREATE OR REPLACE FUNCTION public.account_erasure_dormant_guard() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog SET timezone='UTC' AS $$
BEGIN
  IF current_user::regrole::oid<>__OWNER_OID__ THEN
    RAISE EXCEPTION 'Erasure capability unavailable' USING ERRCODE='42501';
  END IF;
  IF TG_TABLE_NAME='account_erasure_plans' THEN
    IF NOT __CAP__.scope_identity_ok() THEN
      RAISE EXCEPTION 'Erasure source unavailable' USING ERRCODE='42501';
    END IF;
    IF TG_OP='INSERT' AND session_user::regrole::oid=__AUTHORIZER_OID__ THEN
      IF NEW.version IS NOT NULL OR NEW.observed_at>clock_timestamp()
        OR NEW.observed_at<clock_timestamp()-interval '5 seconds'
        OR NEW.scope_nonce IS DISTINCT FROM
          (SELECT scope_nonce FROM public.account_erasure_state WHERE singleton=1) THEN
        RAISE EXCEPTION 'Erasure plan unavailable' USING ERRCODE='42501';
      END IF;
      RETURN NEW;
    ELSIF TG_OP='UPDATE' AND session_user::regrole::oid=__AUTHORIZER_OID__ THEN
      IF OLD.version IS NOT NULL OR NEW.version IS NULL
        OR (to_jsonb(NEW)-'version') IS DISTINCT FROM (to_jsonb(OLD)-'version') THEN
        RAISE EXCEPTION 'Erasure plan immutable' USING ERRCODE='42501';
      END IF;
      RETURN NEW;
    ELSIF TG_OP='DELETE' AND session_user::regrole::oid=__EXECUTOR_OID__ THEN
      IF OLD.expires_at<=clock_timestamp() THEN RETURN OLD; END IF;
    END IF;
    RAISE EXCEPTION 'Erasure plan mutation unavailable' USING ERRCODE='42501';
  END IF;
  -- Preserve the sole immutable bootstrap handoff; jobs and activation stay forbidden.
  IF TG_OP<>'UPDATE' OR TG_TABLE_NAME<>'account_erasure_state' THEN
    RAISE EXCEPTION 'Erasure execution not installed' USING ERRCODE='42501';
  END IF;
  IF NOT __CAP__.scope_identity_ok() OR OLD.original_scope_eligible
    OR NOT NEW.original_scope_eligible OR NEW.owner_oid IS DISTINCT FROM __OWNER_OID__
    OR NEW.executor_oid IS DISTINCT FROM __EXECUTOR_OID__
    OR (to_jsonb(NEW)-ARRAY['original_scope_eligible','owner_oid','executor_oid']) IS DISTINCT FROM
       (to_jsonb(OLD)-ARRAY['original_scope_eligible','owner_oid','executor_oid']) THEN
    RAISE EXCEPTION 'Erasure bootstrap immutable' USING ERRCODE='42501';
  END IF;
  RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION public.account_erasure_dormant_guard() FROM PUBLIC;

CREATE FUNCTION __CAP__.issue_plan(_session uuid,_case uuid,_database oid,_namespace oid,
  _nonce uuid,_correlation uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog SET timezone='UTC' AS $$
DECLARE _actor uuid; _subject uuid; _plan uuid; _observed timestamptz; _expires timestamptz;
  _version text;
BEGIN
  IF session_user::regrole::oid<>__AUTHORIZER_OID__ OR NOT __CAP__.scope_identity_ok()
    OR NOT __CAP__.source_shape_ok()
    OR NOT EXISTS(SELECT 1 FROM __CAP__.control WHERE singleton=1
      AND database_oid=_database AND namespace_oid=_namespace AND source_nonce=_nonce) THEN
    RAISE EXCEPTION 'Erasure plan unavailable' USING ERRCODE='42501';
  END IF;
  IF current_setting('transaction_isolation')<>'repeatable read' THEN
    RAISE EXCEPTION 'Erasure plan snapshot required' USING ERRCODE='42501';
  END IF;
  SELECT a.user_id INTO _actor FROM public.auth_sessions a
    JOIN public.users u ON u.id=a.user_id
    JOIN public.user_roles r ON r.user_id=u.id AND r.role='ADMIN'
    WHERE a.id=_session AND u.status='ACTIVE' AND u.closed_at IS NULL
      AND a.rotated_at IS NULL AND a.revoked_at IS NULL
      AND a.access_expires_at>clock_timestamp() AND a.expires_at>clock_timestamp()
      AND a.authenticated_at<=clock_timestamp()
      AND a.authenticated_at>clock_timestamp()-interval '10 minutes'
      AND r.granted_at<=clock_timestamp()
    FOR SHARE OF a,u,r;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Erasure authority unavailable' USING ERRCODE='42501';
  END IF;
  -- Bind subject from immutable server-owned case metadata before locking case rows.
  SELECT d.user_id INTO _subject FROM public.data_subject_requests d WHERE d.id=_case;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Erasure case unavailable' USING ERRCODE='42501';
  END IF;
  IF NOT pg_catalog.pg_try_advisory_xact_lock_shared(
    pg_catalog.hashtextextended('kasoma.account-processing.v1:' ||
      __NAMESPACE_OID__::oid::text || ':' || _subject::text,0)
      | (-9223372036854775808)::bigint) THEN
    RAISE EXCEPTION 'Erasure source busy' USING ERRCODE='42501';
  END IF;
  SELECT d.user_id INTO _subject FROM public.data_subject_requests d
    JOIN public.data_request_reviews v ON v.request_id=d.id
    JOIN public.users u ON u.id=d.user_id
    WHERE d.id=_case AND d.kind='DELETE' AND d.completed_at IS NULL
      AND d.verification_method='RECENT_OTP' AND d.retention_policy='SIX_YEARS_AFTER_COMPLETION'
      AND d.authenticated_at<=d.created_at AND d.created_at<=clock_timestamp()
      AND v.actor_id=_actor AND d.user_id<>_actor AND u.closed_at IS NULL
    FOR SHARE OF d,v,u;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Erasure case unavailable' USING ERRCODE='42501';
  END IF;
  _plan:=gen_random_uuid(); _observed:=clock_timestamp();
  _expires:=_observed+make_interval(secs=>__PLAN_TTL_SECONDS__);
  INSERT INTO public.account_erasure_plans(id,request_id,scope_nonce,policy,manifest,
    inventory_hash,observed_at,expires_at)
    VALUES(_plan,_case,_nonce,'synthetic-account-erasure-v1','erasure-0045-v1',
      '__MANIFEST_HASH__',_observed,_expires);
  INSERT INTO public.audit_log(id,actor_id,target_id,action,reason,request_id,created_at)
    VALUES(gen_random_uuid(),_actor,_case,'data_request.erasure_plan_read',
      'Minimized erasure plan access',_correlation,clock_timestamp());
  _version:=__CAP__.source_version(_subject,_plan);
  UPDATE public.account_erasure_plans SET version=_version WHERE id=_plan;
  RETURN jsonb_build_object('request_id',_case,'plan_id',_plan,'version',_version,
    'policy','synthetic-account-erasure-v1','manifest','erasure-0045-v1',
    'observed_at',_observed,'expires_at',_expires,'authorization_available',false,
    'blockers',jsonb_build_array('EXECUTION_DISABLED','VERIFICATION_INCOMPLETE'));
END $$;
ALTER FUNCTION __CAP__.issue_plan(uuid,uuid,oid,oid,uuid,uuid) OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.issue_plan(uuid,uuid,oid,oid,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION __CAP__.issue_plan(uuid,uuid,oid,oid,uuid,uuid) TO __AUTHORIZER__;

CREATE FUNCTION __CAP__.expire_plans() RETURNS integer
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog SET timezone='UTC' AS $$
DECLARE _removed integer;
BEGIN
  IF session_user::regrole::oid<>__EXECUTOR_OID__ OR NOT __CAP__.scope_identity_ok()
    OR NOT __CAP__.source_shape_ok() THEN
    RAISE EXCEPTION 'Erasure cleanup unavailable' USING ERRCODE='42501';
  END IF;
  WITH candidates AS MATERIALIZED (
    SELECT id FROM public.account_erasure_plans WHERE expires_at<=clock_timestamp()
      ORDER BY expires_at,id LIMIT 200
  ), due AS MATERIALIZED (
    SELECT p.id FROM public.account_erasure_plans p JOIN candidates c ON c.id=p.id
      ORDER BY p.expires_at,p.id LIMIT 100 FOR UPDATE OF p SKIP LOCKED
  ), removed AS (
    DELETE FROM public.account_erasure_plans p USING due WHERE p.id=due.id RETURNING p.id
  ) SELECT count(*) INTO _removed FROM removed;
  IF _removed>0 THEN
    INSERT INTO public.audit_log(id,actor_id,target_id,action,reason,request_id,created_at)
      SELECT gen_random_uuid(),NULL,installation_nonce,'data_request.erasure_plan_expiry_batch',
        'Expired plan cleanup; removed='||_removed::text,gen_random_uuid(),clock_timestamp()
      FROM __CAP__.control WHERE singleton=1;
  END IF;
  RETURN _removed;
END $$;
ALTER FUNCTION __CAP__.expire_plans() OWNER TO __OWNER__;
REVOKE ALL ON FUNCTION __CAP__.expire_plans() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION __CAP__.expire_plans() TO __EXECUTOR__;
