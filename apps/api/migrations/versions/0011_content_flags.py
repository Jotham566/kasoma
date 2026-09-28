"""FR-GRD-009/FR-CNT-006: bound reports and auditable triage, no evidence mutation."""

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE content_flags (
      id uuid PRIMARY KEY, item_id uuid NOT NULL REFERENCES items(id),
      item_version_id uuid NOT NULL REFERENCES item_versions(id),
      attempt_id uuid NOT NULL REFERENCES attempts(id),
      reporter_id uuid NOT NULL REFERENCES users(id),
      category text NOT NULL CHECK(category IN
        ('QUESTION_ERROR','GRADE_DISPUTE','UNCLEAR','ACCESSIBILITY','UNSAFE_CONTENT','OTHER')),
      comment_encrypted text NOT NULL, report_hash text NOT NULL,
      status text NOT NULL CHECK(status IN ('OPEN','IN_REVIEW','RESOLVED','DISMISSED')),
      priority text NOT NULL CHECK(priority IN ('NORMAL','HIGH')),
      owner_id uuid REFERENCES users(id), revision integer NOT NULL CHECK(revision>=1),
      resolution_encrypted text, created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL,
      resolved_at timestamptz, retention_due_at timestamptz,
      UNIQUE(attempt_id,category),
      CHECK(status='OPEN' OR owner_id IS NOT NULL),
      CHECK((status IN ('RESOLVED','DISMISSED') AND resolution_encrypted IS NOT NULL
        AND resolved_at IS NOT NULL AND retention_due_at=resolved_at + interval '24 months')
        OR (status IN ('OPEN','IN_REVIEW') AND resolution_encrypted IS NULL
          AND resolved_at IS NULL AND retention_due_at IS NULL)));
    CREATE INDEX content_flags_item ON content_flags(item_id);
    CREATE INDEX content_flags_status ON content_flags(status,id);
    CREATE INDEX content_flags_retention ON content_flags(retention_due_at)
      WHERE retention_due_at IS NOT NULL;
    CREATE TABLE content_flag_history (
      id uuid PRIMARY KEY, flag_id uuid NOT NULL REFERENCES content_flags(id),
      actor_id uuid NOT NULL REFERENCES users(id), revision integer NOT NULL,
      status text NOT NULL, priority text NOT NULL, owner_id uuid REFERENCES users(id),
      resolution_hash text, created_at timestamptz NOT NULL, UNIQUE(flag_id,revision));
    CREATE TABLE content_flag_receipts (
      actor_id uuid NOT NULL REFERENCES users(id), key uuid NOT NULL, request_hash text NOT NULL,
      flag_id uuid NOT NULL REFERENCES content_flags(id), PRIMARY KEY(actor_id,key));
    CREATE TRIGGER immutable_flag_history BEFORE UPDATE OR DELETE ON content_flag_history
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE TRIGGER immutable_flag_receipt BEFORE UPDATE OR DELETE ON content_flag_receipts
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE FUNCTION flag_binding_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='INSERT' THEN
        IF NEW.status<>'OPEN' OR NEW.revision<>1 OR NEW.owner_id IS NOT NULL OR NOT EXISTS(
          SELECT 1 FROM attempts a JOIN item_versions v ON v.id=a.item_version_id
          WHERE a.id=NEW.attempt_id AND a.learner_id=NEW.reporter_id
          AND a.item_version_id=NEW.item_version_id AND v.item_id=NEW.item_id)
        THEN RAISE EXCEPTION 'Invalid flag source'; END IF;
      ELSE
        IF (NEW.item_id,NEW.item_version_id,NEW.attempt_id,NEW.reporter_id,NEW.category,
            NEW.comment_encrypted,NEW.report_hash,NEW.created_at) IS DISTINCT FROM
           (OLD.item_id,OLD.item_version_id,OLD.attempt_id,OLD.reporter_id,OLD.category,
            OLD.comment_encrypted,OLD.report_hash,OLD.created_at)
          OR NEW.revision<>OLD.revision+1 OR NEW.status='OPEN'
        THEN RAISE EXCEPTION 'Immutable report or invalid triage revision'; END IF;
      END IF;
      IF NEW.owner_id IS NOT NULL AND (NOT EXISTS(SELECT 1 FROM user_roles
        WHERE user_id=NEW.owner_id AND role IN ('ACADEMIC_REVIEWER','ADMIN'))
        OR EXISTS(SELECT 1 FROM item_versions WHERE id=NEW.item_version_id
          AND author_id=NEW.owner_id))
      THEN RAISE EXCEPTION 'Flag owner must be an independent reviewer'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_flag BEFORE INSERT OR UPDATE ON content_flags
      FOR EACH ROW EXECUTE FUNCTION flag_binding_guard();
    CREATE FUNCTION flag_history_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM content_flags f WHERE f.id=NEW.flag_id
        AND (f.revision,f.status,f.priority,f.owner_id,f.updated_at) IS NOT DISTINCT FROM
            (NEW.revision,NEW.status,NEW.priority,NEW.owner_id,NEW.created_at)
        AND ((NEW.revision=1 AND NEW.actor_id=f.reporter_id) OR
             (NEW.revision>1 AND NEW.actor_id=f.owner_id)))
      THEN RAISE EXCEPTION 'Invalid flag history'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_flag_history BEFORE INSERT ON content_flag_history
      FOR EACH ROW EXECUTE FUNCTION flag_history_guard();
    CREATE FUNCTION flag_audit_required() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM content_flag_history h
        WHERE h.flag_id=NEW.id AND h.revision=NEW.revision)
      THEN RAISE EXCEPTION 'Flag mutation requires history'; END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER complete_flag_history AFTER INSERT OR UPDATE ON content_flags
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION flag_audit_required();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve reports and audit history; use a forward fix")
