CREATE OR REPLACE FUNCTION operations_configuration_version_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE rule record; found_count integer; current_revision integer; previous_values jsonb;
  previous_reference text;
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
  IF current_revision>0 THEN
    SELECT v.thresholds,v.version_ref INTO previous_values,previous_reference
      FROM __SCHEMA__.operations_configuration_state s
      JOIN __SCHEMA__.operations_configuration_versions v ON v.id=s.current_id WHERE s.id=1;
    IF NEW.previous_ref IS DISTINCT FROM previous_reference OR
      (NEW.thresholds - NEW.changed_key) IS DISTINCT FROM
      (previous_values - NEW.changed_key) THEN
      RAISE EXCEPTION 'Operational configuration requires the current single-key version'
        USING ERRCODE='23514';
    END IF;
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
