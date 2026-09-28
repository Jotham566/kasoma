"""FR-DIAG/FR-MST: diagnostic sessions and append-only versioned mastery evidence."""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE assessment_sessions ADD COLUMN kind text NOT NULL DEFAULT 'REVISION'
      CHECK(kind IN ('REVISION','DIAGNOSTIC'));
    ALTER TABLE assessment_sessions ADD COLUMN diagnostic_result json;
    ALTER TABLE assessment_sessions ALTER COLUMN topic_id DROP NOT NULL;
    ALTER TABLE assessment_sessions DROP CONSTRAINT assessment_sessions_item_count_check;
    ALTER TABLE assessment_sessions ADD CONSTRAINT assessment_kind_count CHECK (
      (kind='REVISION' AND topic_id IS NOT NULL AND item_count BETWEEN 5 AND 10) OR
      (kind='DIAGNOSTIC' AND topic_id IS NULL AND item_count BETWEEN 10 AND 15));
    CREATE UNIQUE INDEX one_active_diagnostic ON assessment_sessions(learner_id,subject_id)
      WHERE kind='DIAGNOSTIC' AND status='ACTIVE';
    ALTER TABLE session_items DROP CONSTRAINT session_items_position_check;
    ALTER TABLE session_items ADD CONSTRAINT bounded_position CHECK(position BETWEEN 1 AND 15);
    ALTER TABLE assessment_outbox_events DROP CONSTRAINT assessment_outbox_events_type_check;
    ALTER TABLE assessment_outbox_events ADD CONSTRAINT assessment_outbox_events_type_check
      CHECK(type IN
      ('session.started','item.served','attempt.graded','session.completed','session.abandoned',
       'diagnostic.started','diagnostic.completed','mastery.updated'));
    CREATE TABLE mastery_evidence (
      id uuid PRIMARY KEY, learner_id uuid NOT NULL REFERENCES users,
      attempt_id uuid NOT NULL REFERENCES grades(attempt_id),
      concept_id uuid NOT NULL REFERENCES concepts,
      competency_id uuid NOT NULL REFERENCES competencies,
      occurred_at timestamptz NOT NULL, snapshot json NOT NULL,
      UNIQUE(attempt_id,concept_id,competency_id),
      CHECK((snapshot->>'score')::numeric BETWEEN 0 AND 1),
      CHECK((snapshot->>'base_weight')::numeric >= 0));
    CREATE INDEX mastery_learner_skill ON mastery_evidence(learner_id,concept_id,competency_id);
    CREATE TABLE mastery_estimates (
      learner_id uuid NOT NULL REFERENCES users, concept_id uuid NOT NULL REFERENCES concepts,
      competency_id uuid NOT NULL REFERENCES competencies, snapshot json NOT NULL,
      PRIMARY KEY(learner_id,concept_id,competency_id),
      CHECK((snapshot->>'mastery')::numeric BETWEEN 0 AND 1),
      CHECK((snapshot->>'confidence')::numeric BETWEEN 0 AND 1));
    CREATE TABLE mastery_estimate_history (
      id uuid PRIMARY KEY, evidence_id uuid NOT NULL UNIQUE REFERENCES mastery_evidence,
      snapshot json NOT NULL);
    CREATE TRIGGER immutable_mastery BEFORE UPDATE OR DELETE ON mastery_evidence
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE TRIGGER immutable_mastery_history BEFORE UPDATE OR DELETE ON mastery_estimate_history
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE FUNCTION mastery_evidence_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM attempts a JOIN grades g ON g.attempt_id=a.id
        JOIN item_versions v ON v.id=a.item_version_id
        WHERE a.id=NEW.attempt_id AND a.learner_id=NEW.learner_id
        AND a.submitted_at=NEW.occurred_at
        AND v.document->>'concept_id'=NEW.concept_id::text
        AND EXISTS(SELECT 1 FROM jsonb_array_elements(v.document::jsonb->'competency_mappings') m
          WHERE m->>'competency_id'=NEW.competency_id::text)
        AND NEW.snapshot->'source'->>'attempt_id'=a.id::text
        AND NEW.snapshot->'source'->>'item_version_id'=v.id::text)
      THEN RAISE EXCEPTION 'Mastery evidence does not match grade ownership or mapping'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_mastery BEFORE INSERT ON mastery_evidence
      FOR EACH ROW EXECUTE FUNCTION mastery_evidence_guard();
    CREATE FUNCTION diagnostic_result_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF OLD.diagnostic_result IS NOT NULL AND
        NEW.diagnostic_result::jsonb IS DISTINCT FROM OLD.diagnostic_result::jsonb
      THEN RAISE EXCEPTION 'Diagnostic result is immutable'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER fixed_diagnostic_result BEFORE UPDATE ON assessment_sessions
      FOR EACH ROW EXECUTE FUNCTION diagnostic_result_guard();
    """)


def downgrade() -> None:
    raise RuntimeError("Learning evidence requires a reviewed forward-fix recovery plan")
