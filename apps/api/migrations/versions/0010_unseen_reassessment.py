"""FR-GRD-008: append-only reassessment linkage and one-item sessions."""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE assessment_sessions DROP CONSTRAINT assessment_sessions_kind_check;
    ALTER TABLE assessment_sessions ADD CHECK(kind IN ('REVISION','DIAGNOSTIC','REASSESSMENT'));
    ALTER TABLE assessment_sessions DROP CONSTRAINT assessment_kind_count;
    ALTER TABLE assessment_sessions ADD CONSTRAINT assessment_kind_count CHECK (
      (kind='REVISION' AND topic_id IS NOT NULL AND item_count BETWEEN 5 AND 10) OR
      (kind='DIAGNOSTIC' AND topic_id IS NULL AND item_count BETWEEN 10 AND 15) OR
      (kind='REASSESSMENT' AND topic_id IS NOT NULL AND item_count=1));
    DROP INDEX assessment_active_topic;
    CREATE UNIQUE INDEX assessment_active_topic ON assessment_sessions(learner_id,topic_id)
      WHERE status='ACTIVE' AND kind='REVISION';
    CREATE TABLE reassessments (
      original_attempt_id uuid PRIMARY KEY REFERENCES attempts(id),
      session_id uuid NOT NULL UNIQUE REFERENCES assessment_sessions(id),
      item_version_id uuid NOT NULL REFERENCES item_versions(id),
      basis text NOT NULL CHECK(basis IN ('EQUIVALENT','SAME_SKILL_DIFFICULTY')),
      elapsed_seconds double precision NOT NULL CHECK(elapsed_seconds>=0),
      snapshot json NOT NULL, input_hash text NOT NULL);
    CREATE TRIGGER immutable_reassessment BEFORE UPDATE OR DELETE ON reassessments
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE FUNCTION reassessment_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM attempts a
        JOIN grades g ON g.attempt_id=a.id
        JOIN session_items original ON original.id=a.session_item_id
        JOIN assessment_sessions parent ON parent.id=original.session_id
        JOIN assessment_sessions child ON child.id=NEW.session_id
        JOIN item_versions target ON target.id=NEW.item_version_id
        JOIN items target_item ON target_item.id=target.item_id
        JOIN item_versions source ON source.id=a.item_version_id
        WHERE a.id=NEW.original_attempt_id AND parent.kind='REVISION'
        AND child.kind='REASSESSMENT' AND child.learner_id=a.learner_id
        AND child.subject_id=parent.subject_id AND child.subject_id=target_item.subject_id
        AND child.topic_id=target.topic_id AND target.status='APPROVED'
        AND source.item_id<>target.item_id AND source.concept_id=target.concept_id
        AND source.document->>'difficulty'=target.document->>'difficulty'
        AND (SELECT m->>'competency_id' FROM json_array_elements(
          source.document->'competency_mappings') m
          ORDER BY (m->>'weight')::numeric DESC,m->>'competency_id' LIMIT 1)
        = (SELECT m->>'competency_id' FROM json_array_elements(
          target.document->'competency_mappings') m
          ORDER BY (m->>'weight')::numeric DESC,m->>'competency_id' LIMIT 1)
        AND target.synthetic AND target.document::jsonb->'channel_suitability' ? 'WEB'
        AND NOT EXISTS(SELECT 1 FROM session_items seen
          JOIN assessment_sessions seen_session ON seen_session.id=seen.session_id
          JOIN item_versions seen_version ON seen_version.id=seen.item_version_id
          WHERE seen_session.learner_id=a.learner_id AND seen_version.item_id=target.item_id
          AND seen.served_at IS NOT NULL)

        AND abs(NEW.elapsed_seconds-extract(epoch FROM child.started_at-a.submitted_at))<0.01
        AND EXISTS(SELECT 1 FROM session_items si WHERE si.session_id=child.id
          AND si.item_version_id=target.id AND si.position=1))
      THEN RAISE EXCEPTION 'Invalid reassessment binding'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_reassessment BEFORE INSERT ON reassessments
      FOR EACH ROW EXECUTE FUNCTION reassessment_guard();
    CREATE FUNCTION reassessment_assignment_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE target_session uuid;
    BEGIN
      IF TG_TABLE_NAME='assessment_sessions' THEN target_session=NEW.id;
      ELSE target_session=NEW.session_id; END IF;
      IF EXISTS(SELECT 1 FROM assessment_sessions WHERE id=target_session AND kind='REASSESSMENT')
        AND ((SELECT COUNT(*) FROM session_items WHERE session_id=target_session)<>1
          OR NOT EXISTS(SELECT 1 FROM reassessments WHERE session_id=target_session))
      THEN RAISE EXCEPTION 'Reassessment needs one bound assignment'; END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER reassessment_session_complete AFTER INSERT ON assessment_sessions
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION reassessment_assignment_guard();
    CREATE CONSTRAINT TRIGGER reassessment_item_count AFTER INSERT ON session_items
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION reassessment_assignment_guard();
    CREATE FUNCTION fixed_reassessment_session() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF (OLD.kind='REASSESSMENT' OR NEW.kind='REASSESSMENT') AND
        (NEW.kind,NEW.learner_id,NEW.subject_id,NEW.topic_id,NEW.item_count,NEW.started_at,
          NEW.plan_version,NEW.reason) IS DISTINCT FROM
        (OLD.kind,OLD.learner_id,OLD.subject_id,OLD.topic_id,OLD.item_count,OLD.started_at,
          OLD.plan_version,OLD.reason)
      THEN RAISE EXCEPTION 'Reassessment plan is immutable'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER fixed_reassessment BEFORE UPDATE ON assessment_sessions
      FOR EACH ROW EXECUTE FUNCTION fixed_reassessment_session();
    ALTER TABLE assessment_outbox_events DROP CONSTRAINT assessment_outbox_events_type_check;
    ALTER TABLE assessment_outbox_events ADD CHECK(type IN
      ('session.started','item.served','attempt.graded','session.completed','session.abandoned',
       'diagnostic.started','diagnostic.completed','mastery.updated','hint.used',
       'reassessment.started','reassessment.completed'));
    """)


def downgrade() -> None:
    raise RuntimeError("Retain original/reassessment evidence and use a forward fix")
