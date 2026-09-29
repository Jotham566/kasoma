"""FR-ID-006: owner export completion, encrypted retry copies and bounded retention."""

from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE data_subject_requests ADD COLUMN completed_at timestamptz;
    ALTER TABLE data_subject_requests ADD COLUMN retention_due_at timestamptz;
    ALTER TABLE data_subject_requests ADD COLUMN export_digest text;
    ALTER TABLE data_subject_requests DROP CONSTRAINT data_subject_requests_user_id_kind_key;
    CREATE UNIQUE INDEX one_pending_data_request ON data_subject_requests(user_id,kind)
      WHERE completed_at IS NULL;
    CREATE TABLE data_exports (
      request_id uuid PRIMARY KEY REFERENCES data_subject_requests(id),
      encrypted_payload text NOT NULL CHECK(length(encrypted_payload) BETWEEN 1 AND 3000000),
      digest text NOT NULL CHECK(digest ~ '^[0-9a-f]{64}$'),
      created_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
      CHECK(expires_at=created_at+interval '24 hours'));
    CREATE INDEX data_exports_expiry ON data_exports(expires_at);
    DROP TRIGGER immutable_data_request ON data_subject_requests;
    CREATE FUNCTION data_request_completion_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Request evidence is retained'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.completed_at IS NOT NULL OR NEW.retention_due_at IS NOT NULL
          OR NEW.export_digest IS NOT NULL
          THEN RAISE EXCEPTION 'New request must be pending'; END IF;
        RETURN NEW;
      END IF;
      IF (to_jsonb(NEW)-ARRAY['completed_at','retention_due_at','export_digest']) IS DISTINCT FROM
         (to_jsonb(OLD)-ARRAY['completed_at','retention_due_at','export_digest'])
        OR OLD.completed_at IS NOT NULL OR NEW.kind<>'EXPORT'
        OR NEW.completed_at IS NULL OR NEW.completed_at<NEW.created_at
        OR NEW.retention_due_at IS NULL
        OR NEW.retention_due_at<>NEW.completed_at+interval '6 years'
        OR NEW.export_digest IS NULL
        OR NOT EXISTS(SELECT 1 FROM data_exports e WHERE e.request_id=NEW.id
          AND e.created_at=NEW.completed_at AND e.digest=NEW.export_digest)
      THEN RAISE EXCEPTION 'Invalid export completion'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER immutable_data_request BEFORE INSERT OR UPDATE OR DELETE ON data_subject_requests
      FOR EACH ROW EXECUTE FUNCTION data_request_completion_guard();
    CREATE FUNCTION data_export_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' THEN RAISE EXCEPTION 'Export is immutable'; END IF;
      IF TG_OP='DELETE' THEN
        IF OLD.expires_at>current_timestamp THEN RAISE EXCEPTION 'Export not expired'; END IF;
        RETURN OLD;
      END IF;
      IF NOT EXISTS(SELECT 1 FROM data_subject_requests r WHERE r.id=NEW.request_id
        AND r.kind='EXPORT' AND r.completed_at IS NULL AND r.created_at<=NEW.created_at)
      THEN RAISE EXCEPTION 'Export needs pending owned request'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_export BEFORE INSERT OR UPDATE OR DELETE ON data_exports
      FOR EACH ROW EXECUTE FUNCTION data_export_guard();
    CREATE FUNCTION export_requires_completion() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM data_subject_requests r WHERE r.id=NEW.request_id
        AND r.completed_at=NEW.created_at AND r.export_digest=NEW.digest)
      THEN RAISE EXCEPTION 'Export requires atomic completion'; END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER export_completion AFTER INSERT ON data_exports
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION export_requires_completion();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve completed request evidence and use a forward fix")
