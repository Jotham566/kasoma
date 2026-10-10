"""FR-GRD-004: durable one-claim work with immutable transition evidence; no delivery enablement."""

from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE assessment_grading_work (
      attempt_id uuid PRIMARY KEY REFERENCES attempts,
      correlation_id uuid NOT NULL,
      revision integer NOT NULL DEFAULT 1 CHECK(revision BETWEEN 1 AND 3),
      status text NOT NULL CHECK(status IN ('QUEUED','RUNNING','GRADED','LOW_CONFIDENCE')),
      queued_at timestamptz NOT NULL,
      claim_id uuid UNIQUE,
      claimed_at timestamptz,
      lease_until timestamptz,
      finished_at timestamptz,
      reason text CHECK(reason IN
        ('QUEUE_EXPIRED','WORKER_EXPIRED','NOT_ELIGIBLE','GRADING_FAILED')),
      CHECK((claim_id IS NULL)=(claimed_at IS NULL) AND (claim_id IS NULL)=(lease_until IS NULL)),
      CHECK(claimed_at IS NULL OR (claimed_at>=queued_at
        AND claimed_at<queued_at+interval '5 minutes'
        AND lease_until=least(claimed_at+interval '30 seconds',queued_at+interval '5 minutes'))),
      CHECK(status<>'QUEUED' OR claim_id IS NULL),
      CHECK(status NOT IN ('RUNNING','GRADED') OR claim_id IS NOT NULL),
      CHECK((status IN ('GRADED','LOW_CONFIDENCE'))=(finished_at IS NOT NULL)),
      CHECK((status='LOW_CONFIDENCE')=(reason IS NOT NULL)),
      CHECK(finished_at IS NULL OR finished_at>=coalesce(claimed_at,queued_at)),
      CHECK(finished_at IS NULL OR CASE
        WHEN reason='QUEUE_EXPIRED' THEN claim_id IS NULL
          AND finished_at>=queued_at+interval '5 minutes'
        WHEN reason='WORKER_EXPIRED' THEN claim_id IS NOT NULL AND finished_at>=lease_until
        ELSE claim_id IS NOT NULL AND finished_at<lease_until END));
    CREATE INDEX assessment_grading_queue ON assessment_grading_work(queued_at,attempt_id)
      WHERE status='QUEUED';
    CREATE INDEX assessment_grading_expiry ON assessment_grading_work(lease_until,attempt_id)
      WHERE status='RUNNING';
    CREATE TABLE assessment_grading_history (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      attempt_id uuid NOT NULL REFERENCES assessment_grading_work,
      revision integer NOT NULL,
      snapshot jsonb NOT NULL,
      UNIQUE(attempt_id,revision));

    CREATE FUNCTION grading_work_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN
        RAISE EXCEPTION 'Grading accountability requires retention processing'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.status<>'QUEUED' OR NEW.revision<>1 OR EXISTS(
          SELECT 1 FROM grades WHERE attempt_id=NEW.attempt_id)
        THEN RAISE EXCEPTION 'New grading work must be ungraded and queued'; END IF;
      ELSE
        IF NEW.attempt_id<>OLD.attempt_id OR NEW.correlation_id<>OLD.correlation_id
          OR NEW.queued_at<>OLD.queued_at OR NEW.revision<>OLD.revision+1
        THEN RAISE EXCEPTION 'Grading command identity is immutable'; END IF;
        IF NOT ((OLD.status='QUEUED' AND NEW.status IN ('RUNNING','LOW_CONFIDENCE'))
          OR (OLD.status='RUNNING' AND NEW.status IN ('GRADED','LOW_CONFIDENCE')))
        THEN RAISE EXCEPTION 'Invalid grading transition'; END IF;
        IF OLD.status='RUNNING' AND
          (NEW.claim_id,NEW.claimed_at,NEW.lease_until) IS DISTINCT FROM
          (OLD.claim_id,OLD.claimed_at,OLD.lease_until)
        THEN RAISE EXCEPTION 'Grading claim cannot be renewed'; END IF;
        IF OLD.status='QUEUED' AND NEW.status='LOW_CONFIDENCE'
          AND NEW.reason IS DISTINCT FROM 'QUEUE_EXPIRED'
        THEN RAISE EXCEPTION 'Unclaimed work may only expire'; END IF;
      END IF;
      IF NEW.status='GRADED' AND NOT EXISTS(SELECT 1 FROM grades WHERE attempt_id=NEW.attempt_id)
      THEN RAISE EXCEPTION 'Definitive grade must precede publication'; END IF;
      IF NEW.status='LOW_CONFIDENCE' AND EXISTS(
        SELECT 1 FROM grades WHERE attempt_id=NEW.attempt_id)
      THEN RAISE EXCEPTION 'Neutral outcome cannot carry a grade'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_grading_work BEFORE INSERT OR UPDATE OR DELETE
      ON assessment_grading_work FOR EACH ROW EXECUTE FUNCTION grading_work_guard();

    CREATE FUNCTION grading_history_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Grading history is immutable'; END IF;
      IF NOT EXISTS(SELECT 1 FROM assessment_grading_work w
        WHERE w.attempt_id=NEW.attempt_id AND w.revision=NEW.revision AND to_jsonb(w)=NEW.snapshot)
      THEN RAISE EXCEPTION 'Grading history must match current work'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_grading_history BEFORE INSERT OR UPDATE OR DELETE
      ON assessment_grading_history FOR EACH ROW EXECUTE FUNCTION grading_history_guard();
    CREATE FUNCTION record_grading_transition() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      INSERT INTO assessment_grading_history(attempt_id,revision,snapshot)
        VALUES(NEW.attempt_id,NEW.revision,to_jsonb(NEW));
      RETURN NEW;
    END $$;
    CREATE TRIGGER record_grading_transition AFTER INSERT OR UPDATE ON assessment_grading_work
      FOR EACH ROW EXECUTE FUNCTION record_grading_transition();

    CREATE FUNCTION grading_publication_consistent() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF EXISTS(SELECT 1 FROM assessment_grading_work
        WHERE attempt_id=NEW.attempt_id AND status<>'GRADED')
      THEN RAISE EXCEPTION 'Grade and grading-work publication must be atomic'; END IF;
      RETURN NEW;
    END $$;
    CREATE CONSTRAINT TRIGGER grading_publication_consistent AFTER INSERT ON grades
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION grading_publication_consistent();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve grading evidence; disable new work and use a forward fix")
