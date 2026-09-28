"""Add immutable recommended-plan snapshots without rewriting existing sessions."""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE recommendation_snapshots (
      id uuid PRIMARY KEY, learner_id uuid NOT NULL REFERENCES users(id),
      subject_id uuid NOT NULL REFERENCES subjects(id), input_hash text NOT NULL,
      snapshot json NOT NULL, UNIQUE(learner_id, input_hash),
      CHECK(snapshot->>'input_hash'=input_hash));
    CREATE INDEX ix_recommendation_snapshots_learner_id ON recommendation_snapshots(learner_id);
    CREATE TRIGGER recommendation_snapshots_immutable
      BEFORE UPDATE OR DELETE ON recommendation_snapshots
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    ALTER TABLE assessment_sessions ADD COLUMN recommendation_snapshot json;
    ALTER TABLE assessment_sessions ADD CONSTRAINT recommendation_revision_only CHECK (
      recommendation_snapshot IS NULL OR (kind='REVISION' AND
        recommendation_snapshot->>'input_hash' IS NOT NULL AND
        recommendation_snapshot->>'topic_id'=topic_id::text AND
        json_array_length(recommendation_snapshot->'item_version_ids')=item_count));
    CREATE FUNCTION recommendation_snapshot_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.recommendation_snapshot::jsonb IS DISTINCT FROM OLD.recommendation_snapshot::jsonb THEN
        RAISE EXCEPTION 'Recommendation snapshots are immutable';
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER recommendation_snapshot_immutable BEFORE UPDATE ON assessment_sessions
      FOR EACH ROW EXECUTE FUNCTION recommendation_snapshot_guard();
    """)


def downgrade() -> None:
    raise RuntimeError("Retain recommendation audit snapshots; use a forward fix")
