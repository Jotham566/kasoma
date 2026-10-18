"""Blinded review evidence and sticky band disablement; real enablement remains off."""

from alembic import op

revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE grading_publications ADD COLUMN sampling_policy text NOT NULL
      DEFAULT 'global-publication-v1';
    ALTER TABLE grading_publications ADD COLUMN session_ordinal integer;
    ALTER TABLE grading_publications DROP CONSTRAINT grading_publications_check;
    ALTER TABLE grading_publications ADD CONSTRAINT versioned_audit_sampling CHECK (
      (sampling_policy='global-publication-v1' AND session_ordinal IS NULL
        AND audit_required=((ordinal-1)%10=0)) OR
      (sampling_policy='short-text-audit-release-unit-v1' AND session_ordinal BETWEEN 1 AND 15
        AND audit_required=(((ordinal-1)%10=0) OR ((session_ordinal-1)%10=0))));
    ALTER TABLE grading_publication_counters DROP CONSTRAINT grading_publication_counters_check;
    ALTER TABLE grading_publication_counters ADD CONSTRAINT minimum_audit_coverage
      CHECK(assigned_audits BETWEEN (returned_grades+9)/10 AND returned_grades);

    CREATE OR REPLACE FUNCTION grading_publication_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE band grading_bands%ROWTYPE; next_ordinal bigint; model_grade boolean;
      target_session uuid; local_ordinal integer;
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Grading publication is immutable'; END IF;
      SELECT * INTO band FROM grading_bands WHERE id=NEW.band_id FOR UPDATE;
      IF NOT FOUND OR NOT band.enabled OR band.activated_at>NEW.published_at THEN
        RAISE EXCEPTION 'Enabled current band required'; END IF;
      SELECT g.result->>'method'='RUBRIC_MODEL',si.session_id INTO model_grade,target_session
        FROM grades g JOIN attempts a ON a.id=g.attempt_id
        JOIN session_items si ON si.id=a.session_item_id
        JOIN item_versions v ON v.id=a.item_version_id JOIN items i ON i.id=v.item_id
        WHERE a.id=NEW.attempt_id AND a.item_version_id=g.item_version_id
          AND i.subject_id=band.subject_id AND v.topic_id=band.topic_id
          AND a.submitted_at<=NEW.published_at;
      IF NOT FOUND THEN RAISE EXCEPTION 'Publication scope must match definitive grade'; END IF;
      SELECT returned_grades+1 INTO next_ordinal FROM grading_publication_counters
        WHERE band_id=NEW.band_id FOR UPDATE;
      IF NOT FOUND THEN RAISE EXCEPTION 'Publication counter unavailable'; END IF;
      NEW.ordinal:=next_ordinal;
      NEW.audit_required:=((next_ordinal-1)%10=0);
      NEW.sampling_policy:='global-publication-v1';
      NEW.session_ordinal:=NULL;
      IF model_grade THEN
        SELECT count(*)+1 INTO local_ordinal FROM grading_publications p
          JOIN attempts a ON a.id=p.attempt_id JOIN session_items si ON si.id=a.session_item_id
          WHERE p.band_id=NEW.band_id AND si.session_id=target_session;
        NEW.session_ordinal:=local_ordinal;
        NEW.sampling_policy:='short-text-audit-release-unit-v1';
        NEW.audit_required:=NEW.audit_required OR ((local_ordinal-1)%10=0);
      END IF;
      RETURN NEW;
    END $$;

    CREATE TABLE grading_review_counters (
      band_id uuid PRIMARY KEY REFERENCES grading_bands,
      completed_audits bigint NOT NULL DEFAULT 0 CHECK(completed_audits BETWEEN 0 AND 1000000000));
    CREATE TABLE grading_audit_reviews (
      id uuid PRIMARY KEY REFERENCES grading_audit_assignments,
      band_id uuid NOT NULL REFERENCES grading_bands,
      reviewer_id uuid NOT NULL REFERENCES users,
      criterion_points jsonb NOT NULL,
      critical_error text NOT NULL CHECK(critical_error IN
        ('NONE','ACADEMIC_INTEGRITY','SAFEGUARDING','PRIVACY')),
      exact_agreement boolean NOT NULL,
      completion_ordinal bigint NOT NULL CHECK(completion_ordinal BETWEEN 1 AND 1000000000),
      completed_at timestamptz NOT NULL,
      request_key uuid NOT NULL,
      request_hash text NOT NULL CHECK(request_hash ~ '^[0-9a-f]{64}$'),
      correlation_id uuid NOT NULL,
      UNIQUE(band_id,completion_ordinal), UNIQUE(reviewer_id,request_key));

    CREATE FUNCTION grading_review_counter_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Review completion count cannot reset'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.completed_audits<>0 THEN RAISE EXCEPTION 'Review count must start empty'; END IF;
      ELSE
        IF NEW.band_id<>OLD.band_id OR NEW.completed_audits<>OLD.completed_audits+1
          OR NOT EXISTS(SELECT 1 FROM grading_audit_reviews r WHERE r.band_id=NEW.band_id
            AND r.completion_ordinal=NEW.completed_audits)
        THEN RAISE EXCEPTION 'Review evidence must precede counter advancement'; END IF;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_grading_review_counter BEFORE INSERT OR UPDATE OR DELETE
      ON grading_review_counters FOR EACH ROW EXECUTE FUNCTION grading_review_counter_guard();
    INSERT INTO grading_review_counters(band_id) SELECT id FROM grading_bands;
    CREATE FUNCTION initialize_grading_review_counter() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      INSERT INTO grading_review_counters(band_id) VALUES(NEW.id);
      RETURN NEW;
    END $$;
    CREATE TRIGGER initialize_grading_review_counter AFTER INSERT ON grading_bands
      FOR EACH ROW EXECUTE FUNCTION initialize_grading_review_counter();

    CREATE FUNCTION grading_audit_review_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE publication grading_publications%ROWTYPE; assignment grading_audit_assignments%ROWTYPE;
      band grading_bands%ROWTYPE; version item_versions%ROWTYPE; attempt attempts%ROWTYPE;
      model_points jsonb; number_criteria integer; matched integer; next_completion bigint;
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Completed expert review is immutable'; END IF;
      SELECT * INTO assignment FROM grading_audit_assignments WHERE id=NEW.id;
      SELECT * INTO publication FROM grading_publications WHERE attempt_id=assignment.attempt_id;
      SELECT * INTO band FROM grading_bands WHERE id=publication.band_id FOR UPDATE;
      IF NOT FOUND OR NEW.band_id<>band.id THEN
        RAISE EXCEPTION 'Expert review must bind its assigned band'; END IF;
      SELECT * INTO attempt FROM attempts WHERE id=assignment.attempt_id;
      SELECT * INTO version FROM item_versions WHERE id=attempt.item_version_id;
      IF NEW.reviewer_id=attempt.learner_id OR NEW.reviewer_id=version.author_id
        OR EXISTS(SELECT 1 FROM items WHERE id=version.item_id AND author_id=NEW.reviewer_id)
        OR NOT EXISTS(SELECT 1 FROM user_roles r JOIN users u ON u.id=r.user_id
          WHERE r.user_id=NEW.reviewer_id AND r.role='ACADEMIC_REVIEWER' AND u.status='ACTIVE')
      THEN RAISE EXCEPTION 'Independent current academic reviewer required'; END IF;
      SELECT (result::jsonb)->'criterion_points' INTO model_points FROM grades
        WHERE attempt_id=attempt.id AND result->>'method'='RUBRIC_MODEL';
      IF model_points IS NULL OR NEW.completed_at<assignment.assigned_at
        OR NEW.completed_at>clock_timestamp() OR NEW.completed_at<band.updated_at
        OR jsonb_typeof(NEW.criterion_points) IS DISTINCT FROM 'object'
      THEN RAISE EXCEPTION 'Bound complete expert rubric review required'; END IF;
      SELECT count(*) INTO number_criteria FROM jsonb_object_keys(NEW.criterion_points);
      IF number_criteria NOT BETWEEN 1 AND 20 OR EXISTS(
        SELECT 1 FROM jsonb_each(NEW.criterion_points) e
        WHERE jsonb_typeof(e.value)<>'number' OR e.value::text !~ '^(0|[1-9][0-9]*)$')
      THEN RAISE EXCEPTION 'Integer expert criterion points required'; END IF;
      SELECT count(*) INTO matched FROM jsonb_each_text(NEW.criterion_points) e
        JOIN rubric_criteria c ON c.rubric_id=version.id AND c.criterion_id=e.key
        WHERE e.value::integer BETWEEN 0 AND c.maximum_points;
      IF matched<>number_criteria
        OR matched<>(SELECT count(*) FROM rubric_criteria WHERE rubric_id=version.id)
      THEN RAISE EXCEPTION 'Every pinned rubric criterion must be reviewed'; END IF;
      SELECT completed_audits+1 INTO next_completion FROM grading_review_counters
        WHERE band_id=band.id FOR UPDATE;
      IF NOT FOUND THEN RAISE EXCEPTION 'Review completion counter unavailable'; END IF;
      IF EXISTS(SELECT 1 FROM grading_audit_reviews WHERE band_id=band.id
        AND completion_ordinal=next_completion-1 AND completed_at>NEW.completed_at)
      THEN RAISE EXCEPTION 'Review completion time cannot move backwards'; END IF;
      NEW.completion_ordinal:=next_completion;
      NEW.exact_agreement:=(NEW.criterion_points=model_points);
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_grading_audit_review BEFORE INSERT OR UPDATE OR DELETE
      ON grading_audit_reviews FOR EACH ROW EXECUTE FUNCTION grading_audit_review_guard();

    CREATE FUNCTION record_grading_audit_review() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE completed integer; exact integer; critical boolean;
    BEGIN
      UPDATE grading_review_counters SET completed_audits=NEW.completion_ordinal
        WHERE band_id=NEW.band_id;
      SELECT count(*),count(*) FILTER(WHERE exact_agreement),bool_or(critical_error<>'NONE')
        INTO completed,exact,critical FROM (SELECT exact_agreement,critical_error
          FROM grading_audit_reviews WHERE band_id=NEW.band_id
          ORDER BY completion_ordinal DESC LIMIT 100) recent;
      IF critical OR exact*10<completed*9 THEN
        UPDATE grading_bands SET enabled=false,disabled_at=NEW.completed_at,
          updated_at=NEW.completed_at,revision=revision+1,
          disable_reason=CASE WHEN critical THEN 'CRITICAL_ERROR' ELSE 'AUDIT_AGREEMENT' END
          WHERE id=NEW.band_id AND enabled AND disabled_at IS NULL;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER record_grading_audit_review AFTER INSERT ON grading_audit_reviews
      FOR EACH ROW EXECUTE FUNCTION record_grading_audit_review();
    """)

    op.execute("""
    ALTER TABLE legal_holds DROP CONSTRAINT legal_holds_record_type_check;
    ALTER TABLE legal_holds ADD CONSTRAINT legal_holds_record_type_check
      CHECK(record_type IN ('CONSENT','ATTEMPT','CONTENT_FLAG','DATA_REQUEST',
        'GRADE','MASTERY_EVIDENCE','MASTERY_HISTORY','FLAG_HISTORY','DATA_REQUEST_REVIEW',
        'GRADING_HISTORY','GRADING_PUBLICATION','GRADING_AUDIT','GRADING_REVIEW'));
    CREATE OR REPLACE FUNCTION legal_hold_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE owner_id uuid; request_owner uuid; actor uuid;
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
          WHEN 'DATA_REQUEST_REVIEW' THEN SELECT r.user_id INTO owner_id
            FROM data_request_reviews v JOIN data_subject_requests r ON r.id=v.request_id
            WHERE v.request_id=NEW.record_id FOR KEY SHARE OF v,r;
          WHEN 'CONTENT_FLAG' THEN SELECT reporter_id INTO owner_id FROM content_flags
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'DATA_REQUEST' THEN SELECT user_id INTO owner_id FROM data_subject_requests
            WHERE id=NEW.record_id FOR KEY SHARE;
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
    CREATE TRIGGER aa_protect_held_record BEFORE DELETE ON grading_audit_reviews
      FOR EACH ROW EXECUTE FUNCTION protect_held_record('GRADING_REVIEW');
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve expert review evidence and apply a forward fix")
