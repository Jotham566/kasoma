"""FR-CNT-001: durable bounded import command outbox; no existing row transforms."""

from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE content_import_jobs (
      id uuid PRIMARY KEY, actor_id uuid NOT NULL REFERENCES users(id), key uuid NOT NULL,
      request_hash text NOT NULL, request_id uuid NOT NULL, payload jsonb,
      results jsonb NOT NULL DEFAULT '[]', status text NOT NULL DEFAULT 'QUEUED',
      attempts int NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 3), error_code text,
      created_at timestamptz NOT NULL, available_at timestamptz NOT NULL,
      expires_at timestamptz NOT NULL, finished_at timestamptz, UNIQUE(actor_id,key),
      CHECK(isfinite(created_at) AND isfinite(available_at) AND isfinite(expires_at)),
      CHECK(expires_at=created_at+interval '24 hours'),
      CHECK(jsonb_typeof(results)='array' AND jsonb_array_length(results)<=20),
      CHECK((status='QUEUED' AND payload IS NOT NULL AND finished_at IS NULL AND attempts<3)
        OR (status IN ('COMPLETED','FAILED') AND payload IS NULL
          AND finished_at IS NOT NULL AND finished_at>=created_at AND isfinite(finished_at))),
      CHECK(status<>'COMPLETED' OR error_code IS NULL));
    CREATE INDEX content_import_due ON content_import_jobs(available_at) WHERE status='QUEUED';
    CREATE INDEX content_import_owner ON content_import_jobs(actor_id,id);
    CREATE FUNCTION content_import_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Import evidence retained'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.status<>'QUEUED' OR NEW.attempts<>0 OR NEW.results<>'[]'::jsonb
          OR NOT EXISTS(SELECT 1 FROM users u JOIN user_roles r ON r.user_id=u.id
            WHERE u.id=NEW.actor_id AND u.status='ACTIVE' AND r.role='CONTENT_AUTHOR')
        THEN RAISE EXCEPTION 'Active author and queued import required'; END IF;
      ELSE
        IF OLD.status<>'QUEUED' OR
          (to_jsonb(NEW)-ARRAY['payload','results','status','attempts','error_code',
            'available_at','finished_at']) IS DISTINCT FROM
          (to_jsonb(OLD)-ARRAY['payload','results','status','attempts','error_code',
            'available_at','finished_at']) OR NEW.attempts<>OLD.attempts+1
          OR (NEW.payload IS NOT NULL AND NEW.payload IS DISTINCT FROM OLD.payload)
        THEN RAISE EXCEPTION 'Invalid import transition'; END IF;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_content_import BEFORE INSERT OR UPDATE OR DELETE ON content_import_jobs
      FOR EACH ROW EXECUTE FUNCTION content_import_guard();
    """)


def downgrade() -> None:
    raise RuntimeError("Disable import submission/worker and preserve evidence; use a forward fix")
