"""Tighten diagnostic completion and grade-to-evidence bindings without data rewrites."""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE assessment_sessions ADD CONSTRAINT diagnostic_result_completed CHECK(
      diagnostic_result IS NULL OR (kind='DIAGNOSTIC' AND status='COMPLETED'));
    CREATE OR REPLACE FUNCTION mastery_evidence_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM attempts a JOIN grades g ON g.attempt_id=a.id
        JOIN item_versions v ON v.id=a.item_version_id
        WHERE a.id=NEW.attempt_id AND a.learner_id=NEW.learner_id
        AND a.submitted_at=NEW.occurred_at
        AND v.document->>'concept_id'=NEW.concept_id::text
        AND EXISTS(SELECT 1 FROM jsonb_array_elements(v.document::jsonb->'competency_mappings') m
          WHERE m->>'competency_id'=NEW.competency_id::text)
        AND NEW.snapshot->'source'->>'attempt_id'=a.id::text
        AND NEW.snapshot->'source'->>'item_version_id'=v.id::text
        AND NEW.snapshot->'source'->>'concept_id'=NEW.concept_id::text
        AND NEW.snapshot->'source'->>'competency_id'=NEW.competency_id::text
        AND (NEW.snapshot->>'score')::numeric=(g.result->>'score')::numeric
        AND (NEW.snapshot->'source'->>'points_awarded')::numeric=
            (g.result->>'points_awarded')::numeric
        AND (NEW.snapshot->'source'->>'points_possible')::numeric=
            (g.result->>'points_possible')::numeric)

      THEN RAISE EXCEPTION 'Mastery evidence does not match grade ownership or mapping'; END IF;
      RETURN NEW;
    END $$;
    """)


def downgrade() -> None:
    raise RuntimeError("Do not weaken learning-evidence integrity without a recovery plan")
