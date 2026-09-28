"""FR-GRD-001: bounded multiple-choice sets; preserve legacy immutable evidence."""

from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE FUNCTION valid_multiple_response(value jsonb) RETURNS boolean
      LANGUAGE plpgsql IMMUTABLE AS $$
    DECLARE ids jsonb;
    BEGIN
      IF value IS NULL OR jsonb_typeof(value)<>'object'
        OR value->>'type' IS DISTINCT FROM 'MULTIPLE_CHOICE'
        OR NOT value ?& ARRAY['type','choice_ids']
        OR value - ARRAY['type','choice_ids'] <> '{}'::jsonb
        OR jsonb_typeof(value->'choice_ids') IS DISTINCT FROM 'array'
      THEN RETURN false; END IF;
      ids := value->'choice_ids';
      IF jsonb_array_length(ids) NOT BETWEEN 1 AND 8 THEN RETURN false; END IF;
      IF EXISTS(SELECT 1 FROM jsonb_array_elements(ids) e
        WHERE jsonb_typeof(e)<>'string' OR e#>>'{}' !~ '^[A-Z]$')
      THEN RETURN false; END IF;
      RETURN (SELECT count(*)=count(DISTINCT e) AND jsonb_agg(e ORDER BY e)=ids
        FROM jsonb_array_elements(ids) e);
    END $$;
    ALTER TABLE attempts DROP CONSTRAINT bounded_numeric_response;
    ALTER TABLE attempts ADD CONSTRAINT bounded_structured_response CHECK (
      response IS NULL OR valid_multiple_response(response) OR (
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
          (NEW.response IS NOT NULL AND NEW.response->>'type'='NUMERIC'
            AND v.document->>'response_type'='NUMERIC') OR
          (valid_multiple_response(NEW.response) AND v.document->>'response_type'='MULTIPLE_CHOICE'
            AND NOT EXISTS(SELECT 1
              FROM jsonb_array_elements_text(NEW.response->'choice_ids') chosen
              WHERE NOT EXISTS(SELECT 1 FROM json_array_elements(v.document->'choices') option
                WHERE option->>'id'=chosen)))))
      THEN RAISE EXCEPTION 'Attempt does not match an active assignment'; END IF;
      RETURN NEW;
    END $$;
    """)


def downgrade() -> None:
    raise RuntimeError("Retain multiple-choice learning evidence and use a forward fix")
