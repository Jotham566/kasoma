"""Encrypted short-text attempts and atomic rubric publication; runtime defaults off."""

from alembic import op

revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE session_items ADD COLUMN grading_band_id uuid REFERENCES grading_bands(id);
    ALTER TABLE assessment_outbox_events DROP CONSTRAINT assessment_outbox_events_type_check;
    ALTER TABLE assessment_outbox_events ADD CHECK(type IN
      ('session.started','item.served','attempt.saved','attempt.graded','session.completed',
       'session.abandoned','diagnostic.started','diagnostic.completed','mastery.updated',
       'hint.used','reassessment.started','reassessment.completed','attempt.grade_unavailable'));
    CREATE FUNCTION record_neutral_grading_outcome() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.status='LOW_CONFIDENCE' AND OLD.status<>'LOW_CONFIDENCE' THEN
        INSERT INTO assessment_outbox_events(id,session_id,attempt_id,type,version,request_id,
          created_at) SELECT gen_random_uuid(),si.session_id,NEW.attempt_id,
          'attempt.grade_unavailable',1,NEW.correlation_id,NEW.finished_at
          FROM attempts a JOIN session_items si ON si.id=a.session_item_id
          WHERE a.id=NEW.attempt_id;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER record_neutral_grading_outcome AFTER UPDATE ON assessment_grading_work
      FOR EACH ROW EXECUTE FUNCTION record_neutral_grading_outcome();
    CREATE OR REPLACE FUNCTION reject_disabled_short_text() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE version item_versions%ROWTYPE; band grading_bands%ROWTYPE; subject uuid;
    BEGIN
      SELECT * INTO version FROM item_versions WHERE id=NEW.item_version_id;
      IF version.document->>'response_type' IS DISTINCT FROM 'SHORT_TEXT' THEN
        IF NEW.grading_band_id IS NOT NULL THEN
          RAISE EXCEPTION 'Objective assignment cannot carry a grading band'; END IF;
        RETURN NEW;
      END IF;
      IF TG_OP='UPDATE' AND NEW.grading_band_id IS DISTINCT FROM OLD.grading_band_id
      THEN RAISE EXCEPTION 'Assignment grading band is immutable'; END IF;
      IF TG_OP='UPDATE' THEN RETURN NEW; END IF;
      SELECT * INTO band FROM grading_bands WHERE id=NEW.grading_band_id FOR SHARE;
      SELECT subject_id INTO subject FROM items WHERE id=version.item_id;
      IF band.id IS NULL OR NOT band.enabled OR band.activated_at IS NULL
        OR version.status<>'APPROVED' OR band.subject_id<>subject
        OR band.topic_id<>version.topic_id OR band.language<>'en'
        OR NOT EXISTS(SELECT 1 FROM rubrics WHERE id=version.id)
      THEN RAISE EXCEPTION 'Short-text learner delivery is disabled'; END IF;
      RETURN NEW;
    END $$;

    CREATE FUNCTION valid_short_text_response(value jsonb) RETURNS boolean
      LANGUAGE plpgsql IMMUTABLE AS $$
    BEGIN
      RETURN COALESCE(jsonb_typeof(value)='object'
        AND value ?& ARRAY['type','ciphertext','rubric_version_id']
        AND value-ARRAY['type','ciphertext','rubric_version_id']='{}'::jsonb
        AND value->>'type'='SHORT_TEXT'
        AND jsonb_typeof(value->'ciphertext')='string'
        AND length(value->>'ciphertext') BETWEEN 1 AND 24576
        AND value->>'ciphertext' ~ '^[A-Za-z0-9_-]+={0,2}$'
        AND jsonb_typeof(value->'rubric_version_id')='string'
        AND value->>'rubric_version_id' ~
          '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',false);
    END $$;
    ALTER TABLE attempts DROP CONSTRAINT bounded_structured_response;
    ALTER TABLE attempts ADD CONSTRAINT bounded_structured_response CHECK (
      response IS NULL OR valid_multiple_response(response) OR valid_short_text_response(response)
      OR (jsonb_typeof(response)='object'
        AND response ?& ARRAY['type','value','unit']
        AND response-ARRAY['type','value','unit']='{}'::jsonb
        AND response->>'type' IS NOT DISTINCT FROM 'NUMERIC'
        AND jsonb_typeof(response->'value')='string'
        AND jsonb_typeof(response->'unit')='string'
        AND length(response->>'value') BETWEEN 1 AND 64 AND length(response->>'unit')<=24));
    ALTER TABLE attempts ADD COLUMN rubric_version_id uuid GENERATED ALWAYS AS
      (CASE WHEN response->>'type'='SHORT_TEXT' THEN (response->>'rubric_version_id')::uuid END)
      STORED REFERENCES rubrics(id);
    ALTER TABLE attempts ADD CONSTRAINT pinned_attempt_rubric
      CHECK(rubric_version_id IS NULL OR rubric_version_id=item_version_id);

    CREATE OR REPLACE FUNCTION assessment_attempt_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM session_items si JOIN assessment_sessions s ON s.id=si.session_id
        JOIN item_versions v ON v.id=si.item_version_id
        WHERE si.id=NEW.session_item_id AND si.item_version_id=NEW.item_version_id
        AND s.learner_id=NEW.learner_id AND s.status='ACTIVE' AND si.served_at IS NOT NULL
        AND v.status='APPROVED' AND (
          (NEW.choice_id IS NOT NULL AND v.document->>'response_type'='SINGLE_CHOICE') OR
          (NEW.response IS NOT NULL AND NEW.response->>'type'='NUMERIC'
            AND v.document->>'response_type'='NUMERIC') OR
          (valid_multiple_response(NEW.response) AND v.document->>'response_type'='MULTIPLE_CHOICE'
            AND NOT EXISTS(SELECT 1
              FROM jsonb_array_elements_text(NEW.response->'choice_ids') chosen
              WHERE NOT EXISTS(SELECT 1 FROM json_array_elements(v.document->'choices') option
                WHERE option->>'id'=chosen))) OR
          (valid_short_text_response(NEW.response) AND v.document->>'response_type'='SHORT_TEXT'
            AND si.grading_band_id IS NOT NULL
            AND NEW.response->>'rubric_version_id'=v.id::text)))
      THEN RAISE EXCEPTION 'Attempt does not match an active assignment'; END IF;
      RETURN NEW;
    END $$;

    CREATE FUNCTION short_text_submission_consistent() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.response->>'type'='SHORT_TEXT' AND (
        NOT EXISTS(SELECT 1 FROM assessment_grading_work WHERE attempt_id=NEW.id)
        OR NOT EXISTS(SELECT 1 FROM assessment_receipts r JOIN session_items si
          ON si.id=NEW.session_item_id WHERE r.attempt_id=NEW.id
            AND r.learner_id=NEW.learner_id AND r.session_id=si.session_id))
      THEN RAISE EXCEPTION 'Encrypted submission, work and receipt must commit atomically'; END IF;
      RETURN NEW;
    END $$;
    CREATE CONSTRAINT TRIGGER short_text_submission_consistent AFTER INSERT ON attempts
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
      EXECUTE FUNCTION short_text_submission_consistent();

    ALTER TABLE grades ADD COLUMN rubric_version_id uuid GENERATED ALWAYS AS
      (CASE WHEN result->>'method'='RUBRIC_MODEL' THEN (result->>'rubric_version_id')::uuid END)
      STORED REFERENCES rubrics(id);
    ALTER TABLE grades ADD CONSTRAINT pinned_grade_rubric
      CHECK(rubric_version_id IS NULL OR rubric_version_id=item_version_id);
    CREATE FUNCTION encrypted_rubric_grade_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE payload jsonb; version item_versions%ROWTYPE; attempt attempts%ROWTYPE;
      band uuid; maximum integer; awarded integer; matched integer; total integer;
      criterion_count integer;
    BEGIN
      payload:=NEW.result::jsonb;
      SELECT * INTO version FROM item_versions WHERE id=NEW.item_version_id;
      IF version.document->>'response_type' IS DISTINCT FROM 'SHORT_TEXT' THEN
        IF payload->>'method'='RUBRIC_MODEL' THEN
          RAISE EXCEPTION 'Rubric grade requires a short-text item'; END IF;
        RETURN NEW;
      END IF;
      SELECT * INTO attempt FROM attempts WHERE id=NEW.attempt_id;
      SELECT grading_band_id INTO band FROM session_items WHERE id=attempt.session_item_id;
      IF NOT payload ?& ARRAY['format','status','method','attempt_id','item_version_id',
        'rubric_version_id','band_id','score','points_awarded','points_possible','confidence',
        'hint_count','highest_hint_level','grader_version','mastery_update_status',
        'criterion_points','ciphertext'] OR
        payload-ARRAY['format','status','method','attempt_id','item_version_id',
        'rubric_version_id','band_id','score','points_awarded','points_possible','confidence',
        'hint_count','highest_hint_level','grader_version','mastery_update_status',
        'criterion_points','ciphertext']<>'{}'::jsonb
        OR payload->>'format' IS DISTINCT FROM 'kasoma-rubric-grade-v1'
        OR payload->>'method' IS DISTINCT FROM 'RUBRIC_MODEL'
        OR payload->>'status' IS DISTINCT FROM 'GRADED'
        OR payload->>'mastery_update_status' IS DISTINCT FROM 'COMPLETED'
        OR payload->>'attempt_id' IS DISTINCT FROM NEW.attempt_id::text
        OR payload->>'item_version_id' IS DISTINCT FROM NEW.item_version_id::text
        OR payload->>'rubric_version_id' IS DISTINCT FROM NEW.item_version_id::text
        OR payload->>'band_id' IS DISTINCT FROM band::text
        OR attempt.item_version_id IS DISTINCT FROM NEW.item_version_id
        OR attempt.response->>'type' IS DISTINCT FROM 'SHORT_TEXT'
        OR NEW.answer_specification_hash IS DISTINCT FROM version.content_hash
        OR payload->>'hint_count' IS DISTINCT FROM attempt.hint_count::text
        OR payload->>'highest_hint_level' IS DISTINCT FROM attempt.highest_hint_level::text
        OR jsonb_typeof(payload->'ciphertext') IS DISTINCT FROM 'string'
        OR length(payload->>'ciphertext') NOT BETWEEN 1 AND 196608
        OR payload->>'ciphertext' !~ '^[A-Za-z0-9_-]+={0,2}$'
        OR jsonb_typeof(payload->'criterion_points') IS DISTINCT FROM 'object'
        OR payload->>'grader_version' IS DISTINCT FROM 'rubric-dual-pass-v1'
      THEN RAISE EXCEPTION 'Bound encrypted rubric result required'; END IF;
      SELECT maximum_points INTO maximum FROM rubrics WHERE id=NEW.item_version_id;
      SELECT count(*) INTO criterion_count FROM jsonb_object_keys(payload->'criterion_points');
      IF criterion_count NOT BETWEEN 1 AND 20
        OR EXISTS(SELECT 1 FROM jsonb_each(payload->'criterion_points') e
          WHERE jsonb_typeof(e.value)<>'number' OR e.value::text !~ '^(0|[1-9][0-9]*)$')
        OR jsonb_typeof(payload->'points_awarded')<>'number'
        OR payload->>'points_awarded' !~ '^(0|[1-9][0-9]*)$'
        OR jsonb_typeof(payload->'points_possible')<>'number'
        OR payload->>'points_possible' !~ '^[1-9][0-9]*$'
        OR jsonb_typeof(payload->'confidence')<>'number'
        OR (payload->>'confidence')::numeric NOT BETWEEN 0 AND 1
        OR jsonb_typeof(payload->'score')<>'number'
      THEN RAISE EXCEPTION 'Bound integer rubric points required'; END IF;
      awarded:=(payload->>'points_awarded')::integer;
      SELECT count(*),sum(e.value::integer) INTO matched,total
        FROM jsonb_each_text(payload->'criterion_points') e
        JOIN rubric_criteria c ON c.rubric_id=NEW.item_version_id AND c.criterion_id=e.key
        WHERE e.value::integer BETWEEN 0 AND c.maximum_points;
      IF maximum IS NULL OR (payload->>'points_possible')::integer<>maximum
        OR matched<>(SELECT count(*) FROM rubric_criteria WHERE rubric_id=NEW.item_version_id)
        OR matched<>criterion_count OR total<>awarded
        OR abs((payload->>'score')::numeric-awarded::numeric/maximum)>0.000000000001
      THEN RAISE EXCEPTION 'Rubric score must match all pinned criterion points'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_encrypted_rubric_grade BEFORE INSERT ON grades
      FOR EACH ROW EXECUTE FUNCTION encrypted_rubric_grade_guard();

    CREATE FUNCTION rubric_publication_consistent() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE document jsonb;
    BEGIN
      IF NEW.result->>'method' IS DISTINCT FROM 'RUBRIC_MODEL' THEN RETURN NEW; END IF;
      SELECT v.document::jsonb INTO document FROM item_versions v WHERE v.id=NEW.item_version_id;
      IF NOT EXISTS(SELECT 1 FROM assessment_grading_work w WHERE w.attempt_id=NEW.attempt_id
          AND w.status='GRADED')
        OR NOT EXISTS(SELECT 1 FROM grading_publications p WHERE p.attempt_id=NEW.attempt_id
          AND p.band_id::text=NEW.result->>'band_id')
        OR EXISTS(SELECT 1 FROM jsonb_array_elements(document->'competency_mappings') m
          WHERE NOT EXISTS(SELECT 1 FROM mastery_evidence e WHERE e.attempt_id=NEW.attempt_id
            AND e.concept_id::text=document->>'concept_id'
            AND e.competency_id::text=m->>'competency_id'))
      THEN RAISE EXCEPTION 'Atomic rubric work, grade, mastery and audit publication required';
      END IF;
      RETURN NEW;
    END $$;
    CREATE CONSTRAINT TRIGGER rubric_publication_consistent AFTER INSERT ON grades
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION rubric_publication_consistent();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve encrypted learner evidence and apply a forward fix")
