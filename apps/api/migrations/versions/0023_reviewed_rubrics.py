"""FR-CNT/FR-GRD-003: version-pinned rubrics; short-text learner delivery stays disabled."""

from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE FUNCTION rubric_text_list_valid(value jsonb, required boolean)
      RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $$
    DECLARE entry jsonb;
    BEGIN
      IF value IS NULL OR jsonb_typeof(value)<>'array' THEN RETURN false; END IF;
      IF jsonb_array_length(value)>10 OR (required AND jsonb_array_length(value)=0)
      THEN RETURN false; END IF;
      FOR entry IN SELECT * FROM jsonb_array_elements(value) LOOP
        IF jsonb_typeof(entry)<>'string' OR length(btrim(entry #>> '{}'))=0
          OR length(entry #>> '{}')>2000 THEN RETURN false; END IF;
      END LOOP;
      RETURN true;
    END $$;
    CREATE TABLE rubrics (
      id uuid PRIMARY KEY REFERENCES item_versions(id),
      maximum_points integer NOT NULL CHECK(maximum_points BETWEEN 1 AND 20));
    CREATE TABLE rubric_criteria (
      rubric_id uuid NOT NULL REFERENCES rubrics(id),
      criterion_id text NOT NULL CHECK(criterion_id ~ '^[A-Za-z][A-Za-z0-9_-]{0,63}$'),
      position integer NOT NULL CHECK(position BETWEEN 1 AND 20),
      maximum_points integer NOT NULL CHECK(maximum_points BETWEEN 1 AND 100),
      criterion_text text NOT NULL
        CHECK(length(btrim(criterion_text))>0 AND length(criterion_text)<=2000),
      acceptable_evidence jsonb NOT NULL CHECK(rubric_text_list_valid(acceptable_evidence,true)),
      common_errors jsonb NOT NULL CHECK(rubric_text_list_valid(common_errors,false)),
      prohibited_inferences jsonb NOT NULL
        CHECK(rubric_text_list_valid(prohibited_inferences,false)),
      PRIMARY KEY(rubric_id,criterion_id), UNIQUE(rubric_id,position));
    CREATE FUNCTION draft_rubric_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE parent uuid; state text;
    BEGIN
      IF TG_TABLE_NAME='rubrics' THEN
        parent := CASE WHEN TG_OP='DELETE' THEN OLD.id ELSE NEW.id END;
        IF TG_OP='UPDATE' AND NEW.id<>OLD.id
        THEN RAISE EXCEPTION 'Rubric parent is immutable'; END IF;
      ELSE
        parent := CASE WHEN TG_OP='DELETE' THEN OLD.rubric_id ELSE NEW.rubric_id END;
        IF TG_OP='UPDATE' AND NEW.rubric_id<>OLD.rubric_id
        THEN RAISE EXCEPTION 'Rubric parent is immutable'; END IF;
      END IF;
      SELECT status INTO state FROM item_versions WHERE id=parent FOR UPDATE;
      IF state IS DISTINCT FROM 'DRAFT' THEN RAISE EXCEPTION 'Rubric is frozen'; END IF;
      IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
    END $$;
    CREATE TRIGGER protect_rubric BEFORE INSERT OR UPDATE OR DELETE ON rubrics
      FOR EACH ROW EXECUTE FUNCTION draft_rubric_guard();
    CREATE TRIGGER protect_rubric_criterion BEFORE INSERT OR UPDATE OR DELETE ON rubric_criteria
      FOR EACH ROW EXECUTE FUNCTION draft_rubric_guard();
    CREATE FUNCTION review_rubric_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE maximum integer; total integer; material jsonb; count_criteria integer; document jsonb;
    BEGIN
      document := NEW.document::jsonb;
      IF NEW.status NOT IN ('IN_REVIEW','APPROVED') THEN RETURN NEW; END IF;
      IF document->>'response_type'='SHORT_TEXT' THEN
        SELECT maximum_points INTO maximum FROM rubrics WHERE id=NEW.id;
        SELECT sum(maximum_points), count(*), jsonb_agg(jsonb_build_object(
          'criterion_id',criterion_id,'maximum_points',maximum_points,
          'criterion_text',criterion_text,'acceptable_evidence',acceptable_evidence,
          'common_errors',common_errors,'prohibited_inferences',prohibited_inferences)
          ORDER BY position) INTO total,count_criteria,material
          FROM rubric_criteria WHERE rubric_id=NEW.id;
        IF maximum IS NULL OR maximum IS DISTINCT FROM (document->>'maximum_points')::integer
          OR total IS DISTINCT FROM maximum OR count_criteria NOT BETWEEN 1 AND 20
          OR material IS DISTINCT FROM document->'rubric'->'criteria'
          OR document->>'partial_credit' IS DISTINCT FROM 'CRITERION_SUM'
          OR document->'choices' IS DISTINCT FROM '[]'::jsonb
          OR document->>'correct_choice_id' IS DISTINCT FROM ''
          OR document->'correct_choice_ids' IS DISTINCT FROM '[]'::jsonb
          OR document->'numeric_spec' IS DISTINCT FROM 'null'::jsonb
        THEN RAISE EXCEPTION 'Complete matching rubric required'; END IF;
      ELSIF EXISTS(SELECT 1 FROM rubrics WHERE id=NEW.id)
        OR (document ? 'rubric' AND document->'rubric'<>'null'::jsonb)
        OR document->>'partial_credit' IS DISTINCT FROM 'ALL_OR_NOTHING'
      THEN RAISE EXCEPTION 'Objective items cannot carry a rubric'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER verify_review_rubric BEFORE INSERT OR UPDATE ON item_versions
      FOR EACH ROW EXECUTE FUNCTION review_rubric_guard();
    CREATE FUNCTION reject_disabled_short_text() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF EXISTS(SELECT 1 FROM item_versions WHERE id=NEW.item_version_id
          AND document->>'response_type'='SHORT_TEXT')
      THEN RAISE EXCEPTION 'Short-text learner delivery is disabled'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER aa_reject_disabled_short_text BEFORE INSERT OR UPDATE ON session_items
      FOR EACH ROW EXECUTE FUNCTION reject_disabled_short_text();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve reviewed rubrics; disable authoring and use a forward fix")
