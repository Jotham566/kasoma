-- Frozen ADR-060 v1: only isolated synthetic scopes can enable execution.
CREATE TABLE IF NOT EXISTS __SCHEMA__.export_retirement_state (
  singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
  enabled boolean NOT NULL DEFAULT false,
  phase smallint NOT NULL DEFAULT 1 CHECK(phase BETWEEN 1 AND 4),
  next_receipt uuid, next_review uuid, next_job uuid, next_request uuid,
  updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
INSERT INTO __SCHEMA__.export_retirement_state(singleton) VALUES(true)
  ON CONFLICT(singleton) DO NOTHING;
-- Reinstallation/restore repair always requires a new explicit opt-in.
UPDATE __SCHEMA__.export_retirement_state SET enabled=false WHERE enabled;
REVOKE ALL ON __SCHEMA__.export_retirement_state FROM PUBLIC;

CREATE OR REPLACE FUNCTION __SCHEMA__.export_retirement_scope() RETURNS boolean
LANGUAGE sql STABLE SET search_path=pg_catalog AS $$
  SELECT '__SCHEMA_NAME__' ~ '^identity_test_[0-9a-f]{32}$' OR
    ('__SCHEMA_NAME__'='public' AND current_database() ~
      '^kasoma_(retirement_test|drill_src|drill_dst)_[0-9a-f]{32}$')
$$;

CREATE OR REPLACE FUNCTION __SCHEMA__.export_retirement_owner_safe() RETURNS boolean
LANGUAGE sql STABLE SET search_path=pg_catalog AS $$
  SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=current_user AND rolname='__OWNER__'
    AND NOT rolcanlogin AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole
    AND NOT rolinherit AND NOT rolreplication AND NOT rolbypassrls)
$$;

CREATE OR REPLACE FUNCTION __SCHEMA__.export_retirement_parent_due(target uuid)
RETURNS boolean LANGUAGE sql VOLATILE SET search_path=pg_catalog,__SCHEMA__,pg_temp
SET timezone='UTC' AS $$
  SELECT EXISTS(SELECT 1 FROM __SCHEMA__.data_subject_requests r WHERE r.id=target
    AND r.kind='EXPORT' AND isfinite(r.created_at) AND isfinite(r.completed_at)
    AND isfinite(r.retention_due_at) AND r.completed_at>=r.created_at
    AND r.retention_policy='SIX_YEARS_AFTER_COMPLETION'
    AND r.retention_due_at=r.completed_at+interval '6 years'
    AND r.retention_due_at<=clock_timestamp()
    AND NOT EXISTS(SELECT 1 FROM __SCHEMA__.data_exports e WHERE e.request_id=r.id)
    AND NOT EXISTS(SELECT 1 FROM __SCHEMA__.personal_export_generations g
      WHERE g.request_id=r.id))
$$;

CREATE OR REPLACE FUNCTION __SCHEMA__.export_retirement_allowed(kind text,target uuid)
RETURNS boolean LANGUAGE plpgsql VOLATILE
SET search_path=pg_catalog,__SCHEMA__,pg_temp AS $$
DECLARE parent uuid;
BEGIN
  IF NOT __SCHEMA__.export_retirement_owner_safe() OR NOT __SCHEMA__.export_retirement_scope()
  THEN RETURN false; END IF;
  IF NOT EXISTS(SELECT 1 FROM __SCHEMA__.export_retirement_state WHERE singleton AND enabled)
  THEN RETURN false; END IF;
  CASE kind
    WHEN 'DATA_REQUEST_RECEIPT' THEN SELECT request_id INTO parent
      FROM __SCHEMA__.data_request_receipts WHERE id=target;
    WHEN 'DATA_REQUEST_REVIEW' THEN SELECT request_id INTO parent
      FROM __SCHEMA__.data_request_reviews WHERE request_id=target;
    WHEN 'EXPORT_JOB_RECEIPT' THEN SELECT request_id INTO parent
      FROM __SCHEMA__.personal_export_jobs WHERE request_id=target AND status='EXPIRED'
        AND grant_family IS NULL AND grant_authenticated_at IS NULL AND generation_id IS NULL;
    WHEN 'DATA_REQUEST' THEN
      parent := target;
      IF EXISTS(SELECT 1 FROM __SCHEMA__.data_request_receipts WHERE request_id=target)
        OR EXISTS(SELECT 1 FROM __SCHEMA__.data_request_reviews WHERE request_id=target)
        OR EXISTS(SELECT 1 FROM __SCHEMA__.personal_export_jobs WHERE request_id=target)
        OR EXISTS(SELECT 1 FROM __SCHEMA__.legal_holds WHERE request_id=target)
      THEN RETURN false; END IF;
    ELSE RETURN false;
  END CASE;
  RETURN parent IS NOT NULL AND __SCHEMA__.export_retirement_parent_due(parent)
    AND NOT __SCHEMA__.record_is_held(kind,target,clock_timestamp());
END $$;

    CREATE OR REPLACE FUNCTION __SCHEMA__.legal_hold_guard() RETURNS trigger LANGUAGE plpgsql
    SET search_path=pg_catalog,__SCHEMA__,pg_temp AS $$
    DECLARE owner_id uuid; request_owner uuid; actor uuid; source_request uuid;
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Hold evidence is retained'; END IF;
      actor := CASE WHEN TG_OP='INSERT' THEN NEW.created_by ELSE NEW.released_by END;
      SELECT r.user_id INTO request_owner FROM data_subject_requests r
        JOIN data_request_reviews v ON v.request_id=r.id
        WHERE r.id=NEW.request_id AND r.kind='DELETE' AND r.completed_at IS NULL
          AND v.actor_id=actor AND r.user_id<>actor;
      IF request_owner IS NULL OR NOT EXISTS(SELECT 1 FROM user_roles
        WHERE user_id=actor AND role='ADMIN')
      THEN RAISE EXCEPTION 'Independent request claimant required'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.released_at IS NOT NULL OR NEW.released_by IS NOT NULL
          OR NEW.release_reference IS NOT NULL
        THEN RAISE EXCEPTION 'New hold must be unreleased'; END IF;
        CASE NEW.record_type
          WHEN 'CONSENT' THEN SELECT user_id INTO owner_id FROM consent_records
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'ATTEMPT' THEN SELECT learner_id INTO owner_id FROM attempts
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'GRADE' THEN SELECT a.learner_id INTO owner_id FROM grades g
            JOIN attempts a ON a.id=g.attempt_id WHERE g.attempt_id=NEW.record_id
            FOR KEY SHARE OF g,a;
          WHEN 'MASTERY_EVIDENCE' THEN SELECT learner_id INTO owner_id FROM mastery_evidence
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'MASTERY_HISTORY' THEN SELECT e.learner_id INTO owner_id
            FROM mastery_estimate_history h JOIN mastery_evidence e ON e.id=h.evidence_id
            WHERE h.id=NEW.record_id FOR KEY SHARE OF h,e;
          WHEN 'GRADING_REVIEW' THEN SELECT a.learner_id INTO owner_id
            FROM grading_audit_reviews r JOIN grading_audit_assignments g ON g.id=r.id
            JOIN attempts a ON a.id=g.attempt_id
            WHERE r.id=NEW.record_id FOR KEY SHARE OF r,g,a;
          WHEN 'GRADING_PUBLICATION' THEN SELECT a.learner_id INTO owner_id
            FROM grading_publications p JOIN attempts a ON a.id=p.attempt_id
            WHERE p.attempt_id=NEW.record_id FOR KEY SHARE OF p,a;
          WHEN 'GRADING_AUDIT' THEN SELECT a.learner_id INTO owner_id
            FROM grading_audit_assignments g JOIN attempts a ON a.id=g.attempt_id
            WHERE g.id=NEW.record_id FOR KEY SHARE OF g,a;
          WHEN 'GRADING_HISTORY' THEN SELECT a.learner_id INTO owner_id
            FROM assessment_grading_history h JOIN attempts a ON a.id=h.attempt_id
            WHERE h.id=NEW.record_id FOR KEY SHARE OF h,a;
          WHEN 'FLAG_HISTORY' THEN SELECT f.reporter_id INTO owner_id
            FROM content_flag_history h JOIN content_flags f ON f.id=h.flag_id
            WHERE h.id=NEW.record_id FOR KEY SHARE OF h,f;
          WHEN 'DATA_REQUEST_RECEIPT','EXPORT_JOB_RECEIPT' THEN
            IF NEW.record_type='DATA_REQUEST_RECEIPT' THEN
              SELECT request_id INTO source_request FROM data_request_receipts
                WHERE id=NEW.record_id;
            ELSE source_request := NEW.record_id; END IF;
            SELECT user_id INTO owner_id FROM data_subject_requests
              WHERE id=source_request AND kind='EXPORT' FOR UPDATE;
            IF owner_id IS NOT NULL THEN
              IF NEW.record_type='DATA_REQUEST_RECEIPT' THEN
                PERFORM 1 FROM data_request_receipts WHERE id=NEW.record_id
                  AND request_id=source_request FOR UPDATE;
              ELSE
                PERFORM 1 FROM personal_export_jobs j WHERE request_id=source_request
                  AND status='EXPIRED' AND grant_family IS NULL
                  AND grant_authenticated_at IS NULL AND generation_id IS NULL
                  AND NOT EXISTS(SELECT 1 FROM personal_export_generations g
                    WHERE g.request_id=j.request_id) FOR UPDATE;
              END IF;
              IF NOT FOUND THEN owner_id := NULL; END IF;
            END IF;
            IF NEW.created_at>clock_timestamp() OR NEW.expires_at<=clock_timestamp()
            THEN owner_id := NULL; END IF;
          WHEN 'DATA_REQUEST_REVIEW' THEN
            SELECT user_id INTO owner_id FROM data_subject_requests
              WHERE id=NEW.record_id FOR UPDATE;
            IF owner_id IS NOT NULL THEN
              PERFORM 1 FROM data_request_reviews WHERE request_id=NEW.record_id FOR UPDATE;
              IF NOT FOUND THEN owner_id := NULL; END IF;
            END IF;
          WHEN 'CONTENT_FLAG' THEN SELECT reporter_id INTO owner_id FROM content_flags
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'DATA_REQUEST' THEN SELECT user_id INTO owner_id FROM data_subject_requests
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'CHANNEL_INBOUND_RECEIPT' THEN SELECT actor_id INTO owner_id
            FROM inbound_messages WHERE id=NEW.record_id AND status<>'QUEUED'
              AND processed_at IS NOT NULL AND sender_encrypted IS NULL
              AND code_hash IS NULL AND reply_encrypted IS NULL
              AND NEW.created_at<=clock_timestamp() FOR UPDATE;
          WHEN 'CHANNEL_OUTBOUND_RECEIPT' THEN SELECT actor_id INTO owner_id
            FROM outbound_messages WHERE id=NEW.record_id AND status<>'PENDING'
              AND recipient_encrypted IS NULL
              AND NEW.created_at<=clock_timestamp() FOR UPDATE;
          WHEN 'CHANNEL_LINK_SNAPSHOT','CHANNEL_CONVERSATION_SNAPSHOT' THEN
            SELECT r.user_id INTO owner_id FROM channel_preservation_snapshots s
              JOIN channel_preservation_bodies b ON b.snapshot_id=s.id
              JOIN data_subject_requests r ON r.id=s.request_id
              WHERE s.id=NEW.record_id AND s.source_kind=NEW.record_type
                AND s.request_id=NEW.request_id AND NEW.created_at<=clock_timestamp()
                AND NEW.expires_at>clock_timestamp() FOR UPDATE OF b;
          ELSE RAISE EXCEPTION 'Unsupported hold record';
        END CASE;
        IF owner_id IS DISTINCT FROM request_owner
          OR NOT EXISTS(SELECT 1 FROM data_request_reviews
            WHERE request_id=NEW.request_id AND created_at<=NEW.created_at)
        THEN RAISE EXCEPTION 'Hold target must belong to requester'; END IF;
      ELSE
        IF (to_jsonb(NEW)-ARRAY['released_at','released_by','release_reference']) IS DISTINCT FROM
           (to_jsonb(OLD)-ARRAY['released_at','released_by','release_reference'])
          OR OLD.released_at IS NOT NULL OR NEW.released_at IS NULL
        THEN RAISE EXCEPTION 'Only one hold release is permitted'; END IF;
      END IF;
      RETURN NEW;
    END $$;

-- Receipt/review UPDATE remains immutable. Exact held DELETE guards still run first.
CREATE OR REPLACE FUNCTION __SCHEMA__.export_retirement_leaf_guard() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,__SCHEMA__,pg_temp AS $$
DECLARE target uuid;
BEGIN
  IF TG_OP='DELETE' AND current_user='__OWNER__' THEN
    IF TG_TABLE_NAME='data_request_receipts' THEN target := OLD.id;
    ELSE target := OLD.request_id; END IF;
    IF __SCHEMA__.export_retirement_allowed(TG_ARGV[0],target) THEN RETURN OLD; END IF;
  END IF;
  RAISE EXCEPTION 'Assessment evidence is append-only';
END $$;
DROP TRIGGER immutable_data_request ON __SCHEMA__.data_request_receipts;
CREATE TRIGGER immutable_data_request BEFORE UPDATE OR DELETE
  ON __SCHEMA__.data_request_receipts FOR EACH ROW
  EXECUTE FUNCTION __SCHEMA__.export_retirement_leaf_guard('DATA_REQUEST_RECEIPT');
DROP TRIGGER immutable_data_request ON __SCHEMA__.data_request_reviews;
CREATE TRIGGER immutable_data_request BEFORE UPDATE OR DELETE
  ON __SCHEMA__.data_request_reviews FOR EACH ROW
  EXECUTE FUNCTION __SCHEMA__.export_retirement_leaf_guard('DATA_REQUEST_REVIEW');

    CREATE OR REPLACE FUNCTION __SCHEMA__.personal_export_job_guard() RETURNS trigger LANGUAGE plpgsql
    SET search_path=pg_catalog,__SCHEMA__,pg_temp AS $$
    BEGIN
      IF TG_OP='DELETE' THEN
        IF current_user='__OWNER__' AND
          __SCHEMA__.export_retirement_allowed('EXPORT_JOB_RECEIPT',OLD.request_id)
        THEN RETURN OLD; END IF;
        RAISE EXCEPTION 'Export job accountability is retained';
      END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.status<>'QUEUED' OR NEW.attempts<>0 OR NEW.failure IS NOT NULL
          OR NEW.created_at<>NEW.queued_at OR NEW.updated_at<>NEW.queued_at
        THEN RAISE EXCEPTION 'New export job must be queued'; END IF;
      ELSE
        IF NEW.request_id<>OLD.request_id OR NEW.created_at<>OLD.created_at
          OR NEW.updated_at<OLD.updated_at
        THEN RAISE EXCEPTION 'Immutable job ownership/time'; END IF;
        IF NOT (
          (OLD.status='QUEUED' AND NEW.status IN ('RUNNING','FAILED')) OR
          (OLD.status='RUNNING' AND NEW.status IN ('QUEUED','FAILED','READY')) OR
          (OLD.status='FAILED' AND NEW.status='QUEUED') OR
          (OLD.status='READY' AND NEW.status='EXPIRED'))
        THEN RAISE EXCEPTION 'Invalid export job transition'; END IF;
        IF NEW.status='RUNNING' AND NEW.attempts<>OLD.attempts+1
          OR NEW.status='QUEUED' AND OLD.status='FAILED' AND NEW.attempts<>0
          OR NEW.status NOT IN ('RUNNING','QUEUED') AND NEW.attempts<>OLD.attempts
          OR NEW.status='QUEUED' AND OLD.status='RUNNING' AND NEW.attempts<>OLD.attempts
        THEN RAISE EXCEPTION 'Invalid export attempt accounting'; END IF;
        IF NOT(OLD.status='FAILED' AND NEW.status='QUEUED') AND NEW.queued_at<>OLD.queued_at
        THEN RAISE EXCEPTION 'Explicit retry required to renew queue time'; END IF;
        IF NOT(OLD.status='FAILED' AND NEW.status='QUEUED')
          AND NEW.correlation_id<>OLD.correlation_id
        THEN RAISE EXCEPTION 'Automatic work retains command correlation'; END IF;
        IF OLD.status IN ('QUEUED','RUNNING') AND NEW.status IN ('QUEUED','RUNNING')
          AND (NEW.grant_family IS DISTINCT FROM OLD.grant_family OR
            NEW.grant_authenticated_at IS DISTINCT FROM OLD.grant_authenticated_at)
        THEN RAISE EXCEPTION 'Automatic work cannot renew authorization'; END IF;
        IF NEW.status='READY' AND NOT export_grant_valid(NEW.request_id,OLD.grant_family,
          OLD.grant_authenticated_at,NEW.updated_at)
        THEN RAISE EXCEPTION 'Publication authorization expired'; END IF;
        IF NEW.status='EXPIRED' AND (NEW.finished_at<>OLD.finished_at OR NOT EXISTS(
          SELECT 1 FROM personal_export_generations g WHERE g.id=OLD.generation_id
            AND g.expires_at<=NEW.updated_at))
        THEN RAISE EXCEPTION 'Live export cannot expire early'; END IF;
      END IF;
      IF NEW.status IN ('QUEUED','RUNNING') AND (NOT export_grant_valid(NEW.request_id,
          NEW.grant_family,NEW.grant_authenticated_at,NEW.updated_at) OR NOT EXISTS(
          SELECT 1 FROM data_subject_requests WHERE id=NEW.request_id AND completed_at IS NULL))
      THEN RAISE EXCEPTION 'Pending owned request and current grant required'; END IF;
      IF NEW.status='RUNNING' AND NOT EXISTS(SELECT 1 FROM personal_export_generations g
        WHERE g.id=NEW.generation_id AND g.request_id=NEW.request_id
          AND g.created_at=NEW.updated_at AND g.published_at IS NULL)
      THEN RAISE EXCEPTION 'Fresh owned generation required'; END IF;
      RETURN NEW;
    END $$;

    CREATE OR REPLACE FUNCTION __SCHEMA__.data_request_completion_guard()
      RETURNS trigger LANGUAGE plpgsql
    SET search_path=pg_catalog,__SCHEMA__,pg_temp AS $$
    BEGIN
      IF TG_OP='DELETE' THEN
        IF current_user='__OWNER__' AND
          __SCHEMA__.export_retirement_allowed('DATA_REQUEST',OLD.id)
        THEN RETURN OLD; END IF;
        RAISE EXCEPTION 'Request evidence is retained';
      END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.completed_at IS NOT NULL OR NEW.retention_due_at IS NOT NULL
          OR NEW.export_digest IS NOT NULL
        THEN RAISE EXCEPTION 'New request must be pending'; END IF;
        RETURN NEW;
      END IF;
      IF (to_jsonb(NEW)-ARRAY['completed_at','retention_due_at','export_digest']) IS DISTINCT FROM
         (to_jsonb(OLD)-ARRAY['completed_at','retention_due_at','export_digest'])
        OR OLD.completed_at IS NOT NULL OR NEW.kind<>'EXPORT'
        OR NEW.completed_at IS NULL OR NEW.completed_at<NEW.created_at
        OR NEW.retention_due_at IS NULL OR NEW.retention_due_at<>NEW.completed_at+interval '6 years'
        OR NEW.export_digest IS NULL OR NOT (
          EXISTS(SELECT 1 FROM data_exports e WHERE e.request_id=NEW.id
            AND e.created_at=NEW.completed_at AND e.digest=NEW.export_digest) OR
          EXISTS(SELECT 1 FROM personal_export_generations g WHERE g.request_id=NEW.id
            AND g.published_at=NEW.completed_at AND g.digest=NEW.export_digest))
      THEN RAISE EXCEPTION 'Invalid export completion'; END IF;
      RETURN NEW;
    END $$;


CREATE OR REPLACE FUNCTION __SCHEMA__.retire_completed_export_evidence() RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,__SCHEMA__,pg_temp
SET lock_timeout='100ms' SET statement_timeout='2000ms' SET timezone='UTC' AS $$
DECLARE
  state __SCHEMA__.export_retirement_state%ROWTYPE;
  batch uuid := gen_random_uuid(); started timestamptz := clock_timestamp();
  relation_name text; key_name text; kind text; candidate uuid; parent uuid; locked uuid;
  boundary uuid; candidates uuid[]; position integer; examined integer := 0;
  removed integer := 0; row_count integer; next_candidate uuid;
  held integer := 0; ineligible integer := 0; dependency integer := 0; busy integer := 0;
  capped boolean := false; counts jsonb; skips jsonb; result jsonb;
BEGIN
  -- Fail closed if restore strips ownership/ACLs. Neither a GUC nor the caller clock
  -- can authorize work, and review/production public schemas are never eligible.
  IF NOT __SCHEMA__.export_retirement_owner_safe() OR NOT __SCHEMA__.export_retirement_scope()
  THEN RAISE EXCEPTION 'Retirement capability unavailable' USING ERRCODE='42501'; END IF;
  BEGIN
    SELECT * INTO STRICT state FROM __SCHEMA__.export_retirement_state
      WHERE singleton FOR UPDATE NOWAIT;
  EXCEPTION WHEN lock_not_available THEN RETURN jsonb_build_object('status','BUSY');
  END;
  IF NOT state.enabled THEN RETURN jsonb_build_object('status','DISABLED'); END IF;
  CASE state.phase
    WHEN 1 THEN relation_name := 'data_request_receipts'; key_name := 'id';
      kind := 'DATA_REQUEST_RECEIPT'; boundary := state.next_receipt;
    WHEN 2 THEN relation_name := 'data_request_reviews'; key_name := 'request_id';
      kind := 'DATA_REQUEST_REVIEW'; boundary := state.next_review;
    WHEN 3 THEN relation_name := 'personal_export_jobs'; key_name := 'request_id';
      kind := 'EXPORT_JOB_RECEIPT'; boundary := state.next_job;
    WHEN 4 THEN relation_name := 'data_subject_requests'; key_name := 'id';
      kind := 'DATA_REQUEST'; boundary := state.next_request;
  END CASE;
  -- All identifiers above are fixed internal literals. Read at most 200 candidate UUIDs, never bodies.
  EXECUTE format('SELECT array_agg(key ORDER BY key) FROM
    (SELECT %I key FROM __SCHEMA__.%I WHERE ($1::uuid IS NULL OR %I >= $1)
      ORDER BY %I LIMIT 200) page',key_name,relation_name,key_name,key_name)
    INTO candidates USING boundary;
  IF candidates IS NULL AND boundary IS NOT NULL THEN
    EXECUTE format('SELECT array_agg(key ORDER BY key) FROM
      (SELECT %I key FROM __SCHEMA__.%I ORDER BY %I LIMIT 200) page',
      key_name,relation_name,key_name) INTO candidates;
  END IF;
  FOR position IN 1..coalesce(array_length(candidates,1),0) LOOP
    IF examined>=200 OR removed>=100 OR clock_timestamp()>=started+interval '5 seconds'
    THEN capped := true; EXIT; END IF;
    candidate := candidates[position]; examined := examined+1;
    IF state.phase=4 THEN parent := candidate;
    ELSE
      EXECUTE format('SELECT request_id FROM __SCHEMA__.%I WHERE %I=$1',
        relation_name,key_name) INTO parent USING candidate;
    END IF;
    locked := NULL;
    SELECT id INTO locked FROM __SCHEMA__.data_subject_requests WHERE id=parent
      FOR UPDATE SKIP LOCKED;
    IF locked IS NULL THEN busy := busy+1; CONTINUE; END IF;
    -- Compatible with exact hold insertion: EXPORT parent before the leaf.
    EXECUTE format('SELECT %I FROM __SCHEMA__.%I WHERE %I=$1 FOR UPDATE SKIP LOCKED',
      key_name,relation_name,key_name) INTO locked USING candidate;
    IF locked IS NULL THEN busy := busy+1; CONTINUE; END IF;
    IF NOT __SCHEMA__.export_retirement_parent_due(parent)
    THEN ineligible := ineligible+1; CONTINUE; END IF;
    IF __SCHEMA__.record_is_held(kind,candidate,clock_timestamp())
    THEN held := held+1; CONTINUE; END IF;
    IF NOT __SCHEMA__.export_retirement_allowed(kind,candidate)
    THEN dependency := dependency+1; CONTINUE; END IF;
    EXECUTE format('DELETE FROM __SCHEMA__.%I WHERE %I=$1',relation_name,key_name)
      USING candidate;
    GET DIAGNOSTICS row_count=ROW_COUNT;
    removed := removed+row_count;
  END LOOP;
  -- Keep a pointer to an existing source, never a removed-ID tombstone. A full
  -- page may overlap its final retained row on the next pass; this still advances
  -- beyond a held prefix. No more than 200 distinct candidates are examined.
  next_candidate := candidates[examined+1];
  IF examined=coalesce(array_length(candidates,1),0) AND examined=200 THEN
    EXECUTE format('SELECT %I FROM __SCHEMA__.%I WHERE %I=ANY($1)
      ORDER BY %I DESC LIMIT 1',key_name,relation_name,key_name,key_name)
      INTO next_candidate USING candidates;
  END IF;
  capped := capped OR coalesce(array_length(candidates,1),0)=200;
  UPDATE __SCHEMA__.export_retirement_state SET
    next_receipt=CASE WHEN state.phase=1 THEN next_candidate ELSE next_receipt END,
    next_review=CASE WHEN state.phase=2 THEN next_candidate ELSE next_review END,
    next_job=CASE WHEN state.phase=3 THEN next_candidate ELSE next_job END,
    next_request=CASE WHEN state.phase=4 THEN next_candidate ELSE next_request END,
    phase=state.phase%4+1, updated_at=clock_timestamp() WHERE singleton;
  counts := jsonb_build_object('data_request_receipts',0,'data_request_reviews',0,
    'personal_export_jobs',0,'data_subject_requests',0) || jsonb_build_object(relation_name,removed);
  skips := jsonb_build_object('HELD',held,'INELIGIBLE',ineligible,'DEPENDENCY',dependency,'BUSY',busy);
  result := jsonb_build_object('status','PROCESSED','batch_id',batch,'examined',examined,
    'removed',counts,'skipped',skips,'exhausted',capped);
  INSERT INTO __SCHEMA__.audit_log(id,actor_id,target_id,action,reason,request_id,
    before_hash,after_hash,created_at) VALUES(batch,NULL,batch,
    'data_request.export_retirement_batch',
    (result-'batch_id')::text,batch,NULL,NULL,clock_timestamp());
  RETURN result;
END $$;

REVOKE ALL ON FUNCTION __SCHEMA__.export_retirement_scope() FROM PUBLIC;
REVOKE ALL ON FUNCTION __SCHEMA__.export_retirement_owner_safe() FROM PUBLIC;
REVOKE ALL ON FUNCTION __SCHEMA__.export_retirement_parent_due(uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION __SCHEMA__.export_retirement_allowed(text,uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION __SCHEMA__.export_retirement_leaf_guard() FROM PUBLIC;
REVOKE ALL ON FUNCTION __SCHEMA__.retire_completed_export_evidence() FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA __SCHEMA__ TO __OWNER__;
GRANT SELECT, DELETE ON __SCHEMA__.data_subject_requests, __SCHEMA__.data_request_receipts,
  __SCHEMA__.data_request_reviews, __SCHEMA__.personal_export_jobs TO __OWNER__;
GRANT SELECT ON __SCHEMA__.data_exports, __SCHEMA__.personal_export_generations,
  __SCHEMA__.legal_holds TO __OWNER__;
GRANT UPDATE(id) ON __SCHEMA__.data_subject_requests,__SCHEMA__.data_request_receipts TO __OWNER__;
GRANT UPDATE(request_id) ON __SCHEMA__.data_request_reviews,__SCHEMA__.personal_export_jobs TO __OWNER__;
GRANT SELECT, UPDATE ON __SCHEMA__.export_retirement_state TO __OWNER__;
GRANT INSERT ON __SCHEMA__.audit_log TO __OWNER__;
GRANT EXECUTE ON FUNCTION __SCHEMA__.export_retirement_scope(),
  __SCHEMA__.export_retirement_owner_safe(),
  __SCHEMA__.export_retirement_parent_due(uuid),__SCHEMA__.export_retirement_allowed(text,uuid)
  TO __OWNER__;
ALTER FUNCTION __SCHEMA__.retire_completed_export_evidence() OWNER TO __OWNER__;
REVOKE CREATE ON SCHEMA __SCHEMA__ FROM __OWNER__;
