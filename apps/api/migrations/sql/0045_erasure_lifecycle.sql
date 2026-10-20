-- ADR-061 staged persistence only. No owner role, executor, activation or closure
-- entrypoint is provisioned by an ordinary application migration.
ALTER TABLE users ADD COLUMN closed_at timestamptz;
ALTER TABLE users ADD CONSTRAINT users_closed_disabled
  CHECK (closed_at IS NULL OR status='DISABLED');

CREATE TABLE account_erasure_state (
  singleton integer PRIMARY KEY CHECK (singleton=1),
  original_scope_eligible boolean NOT NULL DEFAULT false CHECK (NOT original_scope_eligible),
  database_oid bigint NOT NULL CHECK (database_oid>0),
  namespace_oid bigint NOT NULL CHECK (namespace_oid>0),
  owner_oid bigint CHECK (owner_oid IS NULL),
  executor_oid bigint CHECK (executor_oid IS NULL),
  scope_nonce uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  creation_enabled boolean NOT NULL DEFAULT false CHECK (NOT creation_enabled),
  execution_enabled boolean NOT NULL DEFAULT false CHECK (NOT execution_enabled),
  policy varchar(64) NOT NULL CHECK (policy='synthetic-account-erasure-v1'),
  manifest varchar(64) NOT NULL CHECK (manifest='erasure-0045-v1'),
  installed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
INSERT INTO account_erasure_state(singleton,database_oid,namespace_oid,policy,manifest)
SELECT 1,d.oid,n.oid,'synthetic-account-erasure-v1','erasure-0045-v1'
FROM pg_catalog.pg_database d CROSS JOIN pg_catalog.pg_namespace n
WHERE d.datname=current_database() AND n.nspname=current_schema();

CREATE TABLE account_erasure_plans (
  id uuid PRIMARY KEY,
  request_id uuid NOT NULL REFERENCES data_subject_requests(id),
  scope_nonce uuid NOT NULL,
  policy varchar(64) NOT NULL CHECK (policy='synthetic-account-erasure-v1'),
  manifest varchar(64) NOT NULL CHECK (manifest='erasure-0045-v1'),
  inventory_hash varchar(64) NOT NULL CHECK (inventory_hash ~ '^[a-f0-9]{64}$'),
  version varchar(64) CHECK (version ~ '^[a-f0-9]{64}$'),
  observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  expires_at timestamptz NOT NULL,
  CHECK (isfinite(observed_at) AND isfinite(expires_at)
    AND expires_at>observed_at AND expires_at<=observed_at+interval '10 minutes')
);
CREATE INDEX account_erasure_plans_request ON account_erasure_plans(request_id);
CREATE INDEX account_erasure_plans_expiry ON account_erasure_plans(expires_at);

CREATE TABLE account_erasure_jobs (
  request_id uuid PRIMARY KEY REFERENCES data_subject_requests(id),
  subject_id uuid NOT NULL REFERENCES users(id),
  authorized_by uuid NOT NULL REFERENCES users(id),
  decision_reference uuid NOT NULL,
  authorized_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  authenticated_at timestamptz NOT NULL,
  policy varchar(64) NOT NULL CHECK (policy='synthetic-account-erasure-v1'),
  manifest varchar(64) NOT NULL CHECK (manifest='erasure-0045-v1'),
  -- No plan FK: eventual finite plan cleanup must not be blocked by a durable job.
  plan_id uuid NOT NULL,
  plan_version varchar(64) NOT NULL CHECK (plan_version ~ '^[a-f0-9]{64}$'),
  command_key uuid NOT NULL,
  command_hash varchar(64) NOT NULL CHECK (command_hash ~ '^[a-f0-9]{64}$'),
  phase varchar(32) NOT NULL CHECK (phase='AUTHORIZED'),
  blocker varchar(64) CHECK (blocker IN ('EXECUTION_DISABLED','ISOLATED_SCOPE_REQUIRED',
    'SOURCE_MANIFEST_CHANGED','SOURCE_OWNERSHIP_UNCERTAIN','STAFF_PROVENANCE_REQUIRES_REVIEW',
    'EMBEDDED_REFERENCES_REQUIRE_REVIEW','PRESERVATION_INCOMPLETE','EXPORT_DRAIN_REQUIRED',
    'CLAIMANT_AUTHORITY_UNAVAILABLE','PROCESSOR_UNAVAILABLE','VERIFICATION_INCOMPLETE')),
  failure varchar(64) CHECK (failure IN
    ('DATABASE_UNAVAILABLE','BATCH_TIMEOUT','INTEGRITY_CHECK_FAILED')),
  closed_at timestamptz CHECK (closed_at IS NULL),
  completed_at timestamptz CHECK (completed_at IS NULL),
  examined bigint NOT NULL DEFAULT 0 CHECK (examined=0),
  removed bigint NOT NULL DEFAULT 0 CHECK (removed=0),
  batches bigint NOT NULL DEFAULT 0 CHECK (batches=0),
  private_cursor json CHECK (private_cursor IS NULL),
  correlation_id uuid NOT NULL,
  UNIQUE (authorized_by,command_key),
  CHECK (subject_id<>authorized_by),
  CHECK (blocker IS NULL OR failure IS NULL),
  CHECK (isfinite(authorized_at) AND isfinite(authenticated_at)
    AND authenticated_at<=authorized_at AND authenticated_at>=authorized_at-interval '10 minutes')
);
CREATE INDEX account_erasure_jobs_subject ON account_erasure_jobs(subject_id);

CREATE FUNCTION account_erasure_dormant_guard() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
  RAISE EXCEPTION 'Account erasure capability is not installed' USING ERRCODE='42501';
END $$;

CREATE TRIGGER account_erasure_state_dormant
BEFORE INSERT OR UPDATE OR DELETE ON account_erasure_state
FOR EACH ROW EXECUTE FUNCTION account_erasure_dormant_guard();
CREATE TRIGGER account_erasure_state_no_truncate
BEFORE TRUNCATE ON account_erasure_state
FOR EACH STATEMENT EXECUTE FUNCTION account_erasure_dormant_guard();
CREATE TRIGGER account_erasure_plans_dormant
BEFORE INSERT OR UPDATE OR DELETE ON account_erasure_plans
FOR EACH ROW EXECUTE FUNCTION account_erasure_dormant_guard();
CREATE TRIGGER account_erasure_plans_no_truncate
BEFORE TRUNCATE ON account_erasure_plans
FOR EACH STATEMENT EXECUTE FUNCTION account_erasure_dormant_guard();
CREATE TRIGGER account_erasure_jobs_dormant
BEFORE INSERT OR UPDATE OR DELETE ON account_erasure_jobs
FOR EACH ROW EXECUTE FUNCTION account_erasure_dormant_guard();
CREATE TRIGGER account_erasure_jobs_no_truncate
BEFORE TRUNCATE ON account_erasure_jobs
FOR EACH STATEMENT EXECUTE FUNCTION account_erasure_dormant_guard();

CREATE FUNCTION account_erasure_closure_guard() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
  -- Only a later independently guarded capability may introduce a closure clock.
  -- Neither an ordinary login nor the migration role can activate it through DML.
  IF TG_OP='INSERT' THEN
    IF NEW.closed_at IS NOT NULL THEN
      RAISE EXCEPTION 'Account closure capability is not installed' USING ERRCODE='42501';
    END IF;
  ELSIF TG_OP='DELETE' THEN
    IF OLD.closed_at IS NOT NULL THEN
      RAISE EXCEPTION 'Closed identity requires restricted retirement' USING ERRCODE='42501';
    END IF;
    RETURN OLD;
  ELSIF NEW.closed_at IS DISTINCT FROM OLD.closed_at
    OR (OLD.closed_at IS NOT NULL AND
        (NEW.status<>'DISABLED' OR NEW.id IS DISTINCT FROM OLD.id)) THEN
    RAISE EXCEPTION 'Account closure is immutable' USING ERRCODE='42501';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER users_erasure_closure
BEFORE INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION account_erasure_closure_guard();

REVOKE ALL ON account_erasure_state,account_erasure_plans,account_erasure_jobs FROM PUBLIC;
REVOKE ALL ON FUNCTION account_erasure_dormant_guard(),account_erasure_closure_guard() FROM PUBLIC;
