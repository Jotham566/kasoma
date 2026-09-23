"""FR-REV/GRD: additive assessment, immutable answers and transactional outbox."""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE assessment_sessions (
      id uuid PRIMARY KEY, learner_id uuid NOT NULL REFERENCES users,
      subject_id uuid NOT NULL REFERENCES subjects, topic_id uuid NOT NULL REFERENCES topics,
      status text NOT NULL CHECK (status IN ('ACTIVE','COMPLETED','ABANDONED','EXPIRED')),
      item_count int NOT NULL CHECK (item_count BETWEEN 5 AND 10),
      reason text NOT NULL, plan_version text NOT NULL,
      started_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
      completed_at timestamptz, CHECK(expires_at > started_at)
    );
    CREATE INDEX assessment_learner ON assessment_sessions(learner_id, started_at);
    CREATE UNIQUE INDEX assessment_active_topic ON assessment_sessions(learner_id, topic_id)
      WHERE status='ACTIVE';
    CREATE TABLE session_items (
      id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES assessment_sessions,
      item_version_id uuid NOT NULL REFERENCES item_versions,
      position int NOT NULL CHECK(position BETWEEN 1 AND 10), reason text NOT NULL,
      served_at timestamptz, UNIQUE(session_id, position), UNIQUE(session_id, item_version_id)
    );
    CREATE TABLE attempts (
      id uuid PRIMARY KEY, learner_id uuid NOT NULL REFERENCES users,
      session_item_id uuid NOT NULL UNIQUE REFERENCES session_items,
      item_version_id uuid NOT NULL REFERENCES item_versions,
      choice_id text NOT NULL CHECK(choice_id ~ '^[A-Z]$'), submitted_at timestamptz NOT NULL,
      hint_count int NOT NULL CHECK(hint_count=0), channel text NOT NULL CHECK(channel='WEB')
    );
    CREATE INDEX attempts_learner_time ON attempts(learner_id, submitted_at);
    CREATE TABLE grades (
      attempt_id uuid PRIMARY KEY REFERENCES attempts,
      item_version_id uuid NOT NULL REFERENCES item_versions,
      answer_specification_hash text NOT NULL, result json NOT NULL,
      CHECK((result->>'score')::numeric BETWEEN 0 AND 1),
      CHECK((result->>'points_possible')::int > 0),
      CHECK((result->>'points_awarded')::int BETWEEN 0 AND (result->>'points_possible')::int)
    );
    CREATE TABLE assessment_receipts (
      learner_id uuid NOT NULL REFERENCES users, key uuid NOT NULL, request_hash text NOT NULL,
      session_id uuid NOT NULL REFERENCES assessment_sessions,
      attempt_id uuid REFERENCES attempts, PRIMARY KEY(learner_id,key)
    );
    CREATE TABLE assessment_outbox_events (
      id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES assessment_sessions,
      attempt_id uuid REFERENCES attempts, type text NOT NULL CHECK(type IN
        ('session.started','item.served','attempt.graded','session.completed','session.abandoned')),
      version int NOT NULL CHECK(version=1), request_id uuid NOT NULL,
      created_at timestamptz NOT NULL, published_at timestamptz
    );
    CREATE INDEX assessment_event_pending ON assessment_outbox_events(created_at)
      WHERE published_at IS NULL;
    CREATE FUNCTION assessment_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN RAISE EXCEPTION 'Assessment evidence is append-only'; END $$;
    CREATE TRIGGER immutable_attempt BEFORE UPDATE OR DELETE ON attempts
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE TRIGGER immutable_grade BEFORE UPDATE OR DELETE ON grades
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE TRIGGER immutable_assessment_receipt BEFORE UPDATE OR DELETE ON assessment_receipts
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE FUNCTION assessment_assignment_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Assignment is retained'; END IF;
      IF (NEW.id,NEW.session_id,NEW.item_version_id,NEW.position,NEW.reason) IS DISTINCT FROM
         (OLD.id,OLD.session_id,OLD.item_version_id,OLD.position,OLD.reason)
         OR (OLD.served_at IS NOT NULL AND NEW.served_at IS DISTINCT FROM OLD.served_at)
      THEN RAISE EXCEPTION 'Assignment is immutable'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER fixed_assignment BEFORE UPDATE OR DELETE ON session_items
      FOR EACH ROW EXECUTE FUNCTION assessment_assignment_guard();
    CREATE FUNCTION assessment_attempt_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM session_items si JOIN assessment_sessions s ON s.id=si.session_id
        JOIN item_versions v ON v.id=si.item_version_id
        WHERE si.id=NEW.session_item_id AND si.item_version_id=NEW.item_version_id
        AND s.learner_id=NEW.learner_id AND s.status='ACTIVE' AND si.served_at IS NOT NULL
        AND v.status='APPROVED')
      THEN RAISE EXCEPTION 'Attempt does not match an active assignment'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_attempt BEFORE INSERT ON attempts
      FOR EACH ROW EXECUTE FUNCTION assessment_attempt_guard();
    CREATE FUNCTION assessment_grade_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM attempts a JOIN item_versions v ON v.id=a.item_version_id
        WHERE a.id=NEW.attempt_id AND a.item_version_id=NEW.item_version_id
        AND v.content_hash=NEW.answer_specification_hash)
      THEN RAISE EXCEPTION 'Grade version mismatch'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_grade BEFORE INSERT ON grades
      FOR EACH ROW EXECUTE FUNCTION assessment_grade_guard();
    """)


def downgrade() -> None:
    raise RuntimeError("Destructive learning-evidence downgrade requires a reviewed recovery plan")
