"""FR-GRD-002: additive numeric response storage, preserving immutable choice evidence."""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE attempts ADD COLUMN response jsonb;
    ALTER TABLE attempts ALTER COLUMN choice_id DROP NOT NULL;
    ALTER TABLE attempts ADD CONSTRAINT one_response_representation CHECK (
      (choice_id IS NOT NULL AND response IS NULL) OR
      (choice_id IS NULL AND response IS NOT NULL)
    );
    ALTER TABLE attempts ADD CONSTRAINT bounded_numeric_response CHECK (
      response IS NULL OR (
        jsonb_typeof(response) = 'object' AND
        response ?& ARRAY['type','value','unit'] AND
        response - ARRAY['type','value','unit'] = '{}'::jsonb AND
        (response->>'type') IS NOT DISTINCT FROM 'NUMERIC' AND
        jsonb_typeof(response->'value') = 'string' AND
        jsonb_typeof(response->'unit') = 'string' AND
        length(response->>'value') BETWEEN 1 AND 64 AND
        length(response->>'unit') <= 24
      )
    );
    CREATE OR REPLACE FUNCTION assessment_attempt_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM session_items si JOIN assessment_sessions s ON s.id=si.session_id
        JOIN item_versions v ON v.id=si.item_version_id
        WHERE si.id=NEW.session_item_id AND si.item_version_id=NEW.item_version_id
        AND s.learner_id=NEW.learner_id AND s.status='ACTIVE' AND si.served_at IS NOT NULL
        AND v.status='APPROVED' AND (
          (NEW.choice_id IS NOT NULL AND v.document->>'response_type'='SINGLE_CHOICE') OR
          (NEW.response IS NOT NULL AND v.document->>'response_type'='NUMERIC')))
      THEN RAISE EXCEPTION 'Attempt does not match an active assignment'; END IF;
      RETURN NEW;
    END $$;
    """)


def downgrade() -> None:
    raise RuntimeError("Numeric learning evidence must not be removed without a recovery plan")
