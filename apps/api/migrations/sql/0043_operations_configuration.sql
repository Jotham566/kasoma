CREATE TABLE operations_configuration_versions (
  id uuid PRIMARY KEY,
  revision integer NOT NULL UNIQUE CHECK (revision > 0),
  thresholds jsonb NOT NULL CHECK (octet_length(thresholds::text)<=4096),
  version_ref text NOT NULL UNIQUE CHECK (version_ref ~ '^[a-f0-9]{64}$'),
  previous_ref text NOT NULL CHECK (previous_ref ~ '^[a-f0-9]{64}$'),
  command_hash text NOT NULL CHECK (command_hash ~ '^[a-f0-9]{64}$'),
  changed_key text NOT NULL,
  reason text NOT NULL CHECK (reason IN
    ('INCREASE_SENSITIVITY','REDUCE_NOISE','REVIEWED_BASELINE')),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE operations_configuration_state (
  id integer PRIMARY KEY CHECK (id=1),
  nonce uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  revision integer NOT NULL DEFAULT 0 CHECK (revision >= 0),
  current_id uuid REFERENCES operations_configuration_versions(id),
  CHECK ((revision=0 AND current_id IS NULL) OR (revision>0 AND current_id IS NOT NULL))
);
INSERT INTO operations_configuration_state(id,revision) VALUES(1,0);

CREATE FUNCTION operations_configuration_version_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE rule record; found_count integer; current_revision integer;
BEGIN
  IF TG_OP <> 'INSERT' THEN
    RAISE EXCEPTION 'Operational configuration history is immutable' USING ERRCODE='42501';
  END IF;
  SELECT revision INTO current_revision FROM __SCHEMA__.operations_configuration_state
    WHERE id=1 FOR UPDATE;
  IF current_revision IS NULL OR NEW.revision<>current_revision+1
    OR jsonb_typeof(NEW.thresholds)<>'object' THEN
    RAISE EXCEPTION 'Invalid operational configuration version' USING ERRCODE='23514';
  END IF;
  SELECT count(*) INTO found_count FROM jsonb_object_keys(NEW.thresholds);
  IF found_count<>15 THEN
    RAISE EXCEPTION 'Invalid operational configuration keys' USING ERRCODE='23514';
  END IF;
  FOR rule IN SELECT * FROM (VALUES
    ('request_p95_ms',1,60000),('request_min_samples',1,10000),
    ('failed_imports',1,10000),('import_age_seconds',60,86400),
    ('unresolved_flags',1,10000),('channel_failures',1,10000),
    ('channel_queue_age_seconds',1,86400),('channel_dispatch_p95_ms',1,60000),
    ('channel_dispatch_min_samples',1,1000),('otp_failures',1,10000),
    ('model_gateway_attempts',1,10000),('grading_age_seconds',1,86400),
    ('export_failures',1,10000),('export_age_seconds',60,86400),
    ('retirement_stall_seconds',120,7200)
  ) AS bounds(key,minimum,maximum)
  LOOP
    IF NOT (NEW.thresholds ? rule.key)
      OR jsonb_typeof(NEW.thresholds->rule.key)<>'number'
      OR (NEW.thresholds->>rule.key) !~ '^[0-9]+$'
      OR (NEW.thresholds->>rule.key)::numeric < rule.minimum
      OR (NEW.thresholds->>rule.key)::numeric > rule.maximum THEN
      RAISE EXCEPTION 'Invalid operational configuration range' USING ERRCODE='23514';
    END IF;
  END LOOP;
  IF NOT (NEW.thresholds ? NEW.changed_key) THEN
    RAISE EXCEPTION 'Unknown operational configuration key' USING ERRCODE='23514';
  END IF;
  NEW.created_at:=clock_timestamp();
  RETURN NEW;
END $$;
CREATE TRIGGER operations_configuration_versions_immutable
BEFORE INSERT OR UPDATE OR DELETE ON operations_configuration_versions
FOR EACH ROW EXECUTE FUNCTION operations_configuration_version_guard();
CREATE TRIGGER operations_configuration_versions_no_truncate
BEFORE TRUNCATE ON operations_configuration_versions
FOR EACH STATEMENT EXECUTE FUNCTION operations_configuration_version_guard();

CREATE FUNCTION operations_configuration_pointer_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP IN ('DELETE','TRUNCATE') THEN
    RAISE EXCEPTION 'Operational configuration pointer is required' USING ERRCODE='42501';
  END IF;
  IF NEW.id<>OLD.id OR NEW.nonce<>OLD.nonce OR NEW.revision<>OLD.revision+1 OR NOT EXISTS (
    SELECT 1 FROM __SCHEMA__.operations_configuration_versions v
    WHERE v.id=NEW.current_id AND v.revision=NEW.revision
  ) THEN
    RAISE EXCEPTION 'Invalid operational configuration pointer' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER operations_configuration_pointer_monotonic
BEFORE UPDATE OR DELETE ON operations_configuration_state
FOR EACH ROW EXECUTE FUNCTION operations_configuration_pointer_guard();
CREATE TRIGGER operations_configuration_state_no_truncate
BEFORE TRUNCATE ON operations_configuration_state
FOR EACH STATEMENT EXECUTE FUNCTION operations_configuration_pointer_guard();

CREATE FUNCTION operations_configuration_commit_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM __SCHEMA__.operations_configuration_state s
    WHERE s.id=1 AND s.revision=NEW.revision AND s.current_id=NEW.id
  ) OR (SELECT count(*) FROM __SCHEMA__.audit_log a
    JOIN __SCHEMA__.users u ON u.id=a.actor_id
    JOIN __SCHEMA__.user_roles r ON r.user_id=u.id AND r.role='ADMIN'
    WHERE a.target_id=NEW.id AND a.action='operations.configuration.changed'
      AND a.reason=NEW.reason AND a.before_hash=NEW.previous_ref
      AND a.after_hash=NEW.version_ref AND a.created_at=NEW.created_at
      AND u.status='ACTIVE')<>1 THEN
    RAISE EXCEPTION 'Operational configuration requires atomic audit and pointer'
      USING ERRCODE='23514';
  END IF;
  RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER operations_configuration_atomic
AFTER INSERT ON operations_configuration_versions
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
EXECUTE FUNCTION operations_configuration_commit_guard();
