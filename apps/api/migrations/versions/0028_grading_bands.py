"""Immutable calibration metadata and one-way band state; no activation endpoint."""

from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE grading_bands (
      id uuid PRIMARY KEY,
      subject_id uuid NOT NULL REFERENCES subjects,
      topic_id uuid NOT NULL REFERENCES topics,
      language text NOT NULL
        CHECK(language='en'),
      model_version text NOT NULL
        CHECK(model_version ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'),
      prompt_version text NOT NULL
        CHECK(prompt_version ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'),
      configuration_version text NOT NULL
        CHECK(configuration_version ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'),
      policy_version text NOT NULL
        CHECK(policy_version='short-text-calibration-v1'),
      minimum_characters integer NOT NULL
        CHECK(minimum_characters BETWEEN 1 AND 2000),
      maximum_characters integer NOT NULL
        CHECK(maximum_characters BETWEEN minimum_characters AND 2000),
      benchmark_id uuid NOT NULL,
      report_sha256 text NOT NULL
        CHECK(report_sha256 ~ '^[0-9a-f]{64}$'),
      benchmark_cases bigint NOT NULL
        CHECK(benchmark_cases BETWEEN 1 AND 1000000000),
      benchmark_within_tolerance bigint NOT NULL
        CHECK(benchmark_within_tolerance BETWEEN 0 AND benchmark_cases),
      held_out_cases bigint NOT NULL
        CHECK(held_out_cases BETWEEN 1 AND 1000000000),
      held_out_exact bigint NOT NULL
        CHECK(held_out_exact BETWEEN 0 AND held_out_cases),
      critical_errors bigint NOT NULL
        CHECK(critical_errors BETWEEN 0 AND 1000000000),
      subgroup_review text NOT NULL
        CHECK(subgroup_review IN ('PENDING','APPROVED','HARMFUL')),
      approval_id uuid,
      approved_at timestamptz,
      enabled boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL,
      activated_at timestamptz,
      disabled_at timestamptz,
      disable_reason text CHECK(disable_reason IN ('CRITICAL_ERROR','AUDIT_AGREEMENT','MANUAL')),
      revision integer NOT NULL
        CHECK(revision BETWEEN 1 AND 3),
      CHECK((approval_id IS NULL)=(approved_at IS NULL)),
      CHECK(approved_at IS NULL OR approved_at<=created_at),
      CHECK(updated_at>=created_at),
      CHECK(activated_at IS NULL OR activated_at>=created_at),
      CHECK(disabled_at IS NULL OR disabled_at>=coalesce(activated_at,created_at)),
      CHECK((disabled_at IS NULL)=(disable_reason IS NULL)),
      CHECK(enabled=(activated_at IS NOT NULL AND disabled_at IS NULL)),
      CHECK(NOT enabled OR (approval_id IS NOT NULL AND critical_errors=0
        AND subgroup_review='APPROVED'
        AND benchmark_within_tolerance*100>=benchmark_cases*85
        AND held_out_exact*10>=held_out_cases*9)));
    CREATE TABLE grading_band_history (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      band_id uuid NOT NULL REFERENCES grading_bands,
      revision integer NOT NULL,
      snapshot jsonb NOT NULL,
      UNIQUE(band_id,revision));

    CREATE FUNCTION grading_band_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN
        RAISE EXCEPTION 'Calibration evidence requires retention review'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.revision<>1 OR NEW.enabled OR NEW.activated_at IS NOT NULL
          OR NEW.disabled_at IS NOT NULL OR NEW.updated_at<>NEW.created_at
          OR NOT EXISTS(SELECT 1 FROM topics WHERE id=NEW.topic_id AND subject_id=NEW.subject_id)
        THEN RAISE EXCEPTION 'New calibration bands must be disabled and scope-bound'; END IF;
      ELSE
        IF (to_jsonb(NEW)-ARRAY['enabled','activated_at','disabled_at',
            'disable_reason','revision','updated_at'])
          IS DISTINCT FROM
          (to_jsonb(OLD)-ARRAY['enabled','activated_at','disabled_at',
            'disable_reason','revision','updated_at'])
          OR NEW.revision<>OLD.revision+1 OR NEW.updated_at<OLD.updated_at
          OR OLD.disabled_at IS NOT NULL
        THEN RAISE EXCEPTION 'Calibration identity and disablement are immutable'; END IF;
        IF NEW.disabled_at IS NOT NULL THEN
          IF NEW.enabled OR NEW.activated_at IS DISTINCT FROM OLD.activated_at
            OR NEW.disabled_at<>NEW.updated_at
          THEN RAISE EXCEPTION 'Invalid band disablement'; END IF;
        ELSIF OLD.activated_at IS NULL AND NEW.activated_at IS NOT NULL THEN
          IF NOT NEW.enabled OR NEW.activated_at<>NEW.updated_at
          THEN RAISE EXCEPTION 'Invalid band activation'; END IF;
        ELSE RAISE EXCEPTION 'Invalid calibration state transition'; END IF;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_grading_band BEFORE INSERT OR UPDATE OR DELETE ON grading_bands
      FOR EACH ROW EXECUTE FUNCTION grading_band_guard();
    CREATE FUNCTION grading_band_history_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Calibration history is immutable'; END IF;
      IF NOT EXISTS(SELECT 1 FROM grading_bands b WHERE b.id=NEW.band_id
        AND b.revision=NEW.revision AND to_jsonb(b)=NEW.snapshot)
      THEN RAISE EXCEPTION 'Calibration history must match band state'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_grading_band_history BEFORE INSERT OR UPDATE OR DELETE
      ON grading_band_history
      FOR EACH ROW EXECUTE FUNCTION grading_band_history_guard();
    CREATE FUNCTION record_grading_band_transition() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      INSERT INTO grading_band_history(band_id,revision,snapshot)
        VALUES(NEW.id,NEW.revision,to_jsonb(NEW));
      RETURN NEW;
    END $$;
    CREATE TRIGGER record_grading_band_transition AFTER INSERT OR UPDATE ON grading_bands
      FOR EACH ROW EXECUTE FUNCTION record_grading_band_transition();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve calibration evidence; disable bands and apply a forward fix")
