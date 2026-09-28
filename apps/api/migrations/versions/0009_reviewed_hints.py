"""Reviewed hint disclosure and frozen independence metadata; no historical rewrites."""

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE hint_uses (
      id uuid PRIMARY KEY, learner_id uuid NOT NULL REFERENCES users(id),
      session_item_id uuid NOT NULL REFERENCES session_items(id),
      level int NOT NULL CHECK(level BETWEEN 1 AND 3),
      phase text NOT NULL CHECK(phase IN ('BEFORE_ANSWER','AFTER_ANSWER')),
      created_at timestamptz NOT NULL, UNIQUE(session_item_id,level));
    CREATE INDEX ix_hint_uses_learner_id ON hint_uses(learner_id);
    CREATE TRIGGER immutable_hint_use BEFORE UPDATE OR DELETE ON hint_uses
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    ALTER TABLE assessment_receipts ADD COLUMN hint_use_id uuid REFERENCES hint_uses(id);
    ALTER TABLE attempts DROP CONSTRAINT attempts_hint_count_check;
    ALTER TABLE attempts ADD COLUMN highest_hint_level int NOT NULL DEFAULT 0;
    ALTER TABLE attempts ADD CONSTRAINT bounded_hints CHECK(
      hint_count BETWEEN 0 AND 3 AND highest_hint_level BETWEEN 0 AND 3);
    CREATE FUNCTION hint_use_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      PERFORM id FROM users WHERE id=NEW.learner_id FOR UPDATE;
      IF NOT EXISTS(SELECT 1 FROM session_items si
        JOIN assessment_sessions s ON s.id=si.session_id
        JOIN item_versions v ON v.id=si.item_version_id
        WHERE si.id=NEW.session_item_id AND s.learner_id=NEW.learner_id
        AND s.kind='REVISION' AND si.served_at IS NOT NULL AND v.status='APPROVED'
        AND NEW.level <= COALESCE(json_array_length(v.document->'hints'),0)
        AND ((NEW.phase='BEFORE_ANSWER' AND s.status='ACTIVE' AND s.expires_at>NEW.created_at
          AND NOT EXISTS(SELECT 1 FROM attempts a WHERE a.session_item_id=si.id)
          AND NOT EXISTS(SELECT 1 FROM session_items prior WHERE prior.session_id=s.id
            AND prior.position<si.position AND NOT EXISTS(SELECT 1 FROM attempts a
              WHERE a.session_item_id=prior.id)))
          OR (NEW.phase='AFTER_ANSWER' AND EXISTS(SELECT 1 FROM attempts a
            WHERE a.session_item_id=si.id))))
        OR NEW.level != (SELECT COALESCE(MAX(level),0)+1 FROM hint_uses
          WHERE session_item_id=NEW.session_item_id)
      THEN RAISE EXCEPTION 'Hint does not match an eligible assignment'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER valid_hint_use BEFORE INSERT ON hint_uses
      FOR EACH ROW EXECUTE FUNCTION hint_use_guard();
    CREATE FUNCTION attempt_hint_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      PERFORM id FROM users WHERE id=NEW.learner_id FOR UPDATE;
      IF NEW.hint_count != (SELECT COUNT(*) FROM hint_uses
          WHERE session_item_id=NEW.session_item_id AND phase='BEFORE_ANSWER')
        OR NEW.highest_hint_level != (SELECT COALESCE(MAX(level),0) FROM hint_uses
          WHERE session_item_id=NEW.session_item_id AND phase='BEFORE_ANSWER')
      THEN RAISE EXCEPTION 'Attempt hint metadata does not match disclosure'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_attempt_hints BEFORE INSERT ON attempts
      FOR EACH ROW EXECUTE FUNCTION attempt_hint_guard();
    CREATE FUNCTION evidence_hint_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM attempts a WHERE a.id=NEW.attempt_id
        AND (NEW.snapshot->'source'->>'hint_count')::int=a.hint_count
        AND COALESCE((NEW.snapshot->'source'->>'highest_hint_level')::int,0)=a.highest_hint_level)
      THEN RAISE EXCEPTION 'Mastery hint metadata does not match attempt'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_evidence_hints BEFORE INSERT ON mastery_evidence
      FOR EACH ROW EXECUTE FUNCTION evidence_hint_guard();
    ALTER TABLE assessment_outbox_events ADD COLUMN hint_count int
      CHECK(hint_count BETWEEN 0 AND 3);
    ALTER TABLE assessment_outbox_events ADD COLUMN highest_hint_level int
      CHECK(highest_hint_level BETWEEN 0 AND 3);
    ALTER TABLE assessment_outbox_events DROP CONSTRAINT assessment_outbox_events_type_check;
    ALTER TABLE assessment_outbox_events ADD CHECK(type IN
      ('session.started','item.served','attempt.graded','session.completed','session.abandoned',
       'diagnostic.started','diagnostic.completed','mastery.updated','hint.used'));
    """)


def downgrade() -> None:
    raise RuntimeError("Retain hint and independence evidence; use a forward fix")
