"""ADR-048: additive private export jobs and once-only artifact publication."""

from alembic import op

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE personal_export_jobs (
      request_id uuid PRIMARY KEY REFERENCES data_subject_requests(id),
      status text NOT NULL CHECK(status IN ('QUEUED','RUNNING','FAILED','READY','EXPIRED')),
      correlation_id uuid NOT NULL,
      created_at timestamptz NOT NULL, queued_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL, finished_at timestamptz,
      next_attempt_at timestamptz, attempts integer NOT NULL CHECK(attempts BETWEEN 0 AND 3),
      failure text CHECK(failure IN ('AUTH_REQUIRED','LIMIT_REACHED','PROCESSING_FAILED',
        'REQUEST_COMPLETED')),
      grant_family uuid, grant_authenticated_at timestamptz, generation_id uuid,
      CHECK(created_at<=queued_at AND queued_at<=updated_at),
      CHECK((status IN ('QUEUED','RUNNING'))=(grant_family IS NOT NULL)),
      CHECK((grant_family IS NULL)=(grant_authenticated_at IS NULL)),
      CHECK((status='QUEUED')=(next_attempt_at IS NOT NULL)),
      CHECK(next_attempt_at IS NULL OR next_attempt_at>=updated_at),
      CHECK(status NOT IN ('READY','EXPIRED') OR failure IS NULL),
      CHECK((status IN ('FAILED','READY','EXPIRED'))=(finished_at IS NOT NULL)),
      CHECK(finished_at IS NULL OR finished_at BETWEEN queued_at AND updated_at),
      CHECK((status IN ('RUNNING','READY'))=(generation_id IS NOT NULL)),
      CHECK(status<>'FAILED' OR failure IS NOT NULL));
    CREATE INDEX personal_export_job_queue ON personal_export_jobs(next_attempt_at,request_id)
      WHERE status='QUEUED';
    CREATE TABLE personal_export_generations (
      id uuid PRIMARY KEY,
      request_id uuid NOT NULL REFERENCES personal_export_jobs(request_id),
      created_at timestamptz NOT NULL, lease_until timestamptz NOT NULL,
      published_at timestamptz, expires_at timestamptz, encrypted_manifest text,
      digest text CHECK(digest ~ '^[0-9a-f]{64}$'),
      size integer CHECK(size BETWEEN 1 AND 16777216),
      UNIQUE(request_id,id),
      CHECK(lease_until=created_at+interval '180 seconds'),
      CHECK((published_at IS NULL)=(expires_at IS NULL)),
      CHECK((published_at IS NULL)=(encrypted_manifest IS NULL)),
      CHECK((published_at IS NULL)=(digest IS NULL)),
      CHECK((published_at IS NULL)=(size IS NULL)),
      CHECK(published_at IS NULL OR (published_at>=created_at AND published_at<lease_until
        AND expires_at=published_at+interval '24 hours'
        AND length(encrypted_manifest) BETWEEN 1 AND 100000)));
    CREATE INDEX personal_export_generation_cleanup ON personal_export_generations(lease_until,id);
    CREATE UNIQUE INDEX one_published_personal_export ON personal_export_generations(request_id)
      WHERE published_at IS NOT NULL;
    ALTER TABLE personal_export_jobs ADD CONSTRAINT export_job_current_generation
      FOREIGN KEY(request_id,generation_id) REFERENCES personal_export_generations(request_id,id)
      DEFERRABLE INITIALLY DEFERRED;

    CREATE FUNCTION export_grant_valid(target uuid,family_id uuid,verified timestamptz,
      at_time timestamptz) RETURNS boolean LANGUAGE sql STABLE AS $$
      SELECT verified<=at_time AND verified+interval '10 minutes'>at_time AND EXISTS(
        SELECT 1 FROM data_subject_requests r JOIN users u ON u.id=r.user_id
          JOIN auth_sessions a ON a.user_id=u.id
        WHERE r.id=target AND r.kind='EXPORT' AND u.status='ACTIVE'
          AND a.family=family_id AND a.authenticated_at=verified
          AND a.revoked_at IS NULL AND a.rotated_at IS NULL AND a.expires_at>at_time)
    $$;

    CREATE FUNCTION personal_export_job_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Export job accountability is retained'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.status<>'QUEUED' OR NEW.attempts<>0 OR NEW.failure IS NOT NULL
          OR NEW.created_at<>NEW.queued_at OR NEW.updated_at<>NEW.queued_at
        THEN RAISE EXCEPTION 'New export job must be queued'; END IF;
      ELSE
        IF NEW.request_id<>OLD.request_id OR NEW.created_at<>OLD.created_at
          OR NEW.updated_at<OLD.updated_at
        THEN RAISE EXCEPTION 'Immutable job ownership/time'; END IF;
        IF NOT (
          (OLD.status='QUEUED' AND NEW.status IN ('RUNNING','FAILED')) OR
          (OLD.status='RUNNING' AND NEW.status IN ('QUEUED','FAILED','READY')) OR
          (OLD.status='FAILED' AND NEW.status='QUEUED') OR
          (OLD.status='READY' AND NEW.status='EXPIRED'))
        THEN RAISE EXCEPTION 'Invalid export job transition'; END IF;
        IF NEW.status='RUNNING' AND NEW.attempts<>OLD.attempts+1
          OR NEW.status='QUEUED' AND OLD.status='FAILED' AND NEW.attempts<>0
          OR NEW.status NOT IN ('RUNNING','QUEUED') AND NEW.attempts<>OLD.attempts
          OR NEW.status='QUEUED' AND OLD.status='RUNNING' AND NEW.attempts<>OLD.attempts
        THEN RAISE EXCEPTION 'Invalid export attempt accounting'; END IF;
        IF NOT(OLD.status='FAILED' AND NEW.status='QUEUED') AND NEW.queued_at<>OLD.queued_at
        THEN RAISE EXCEPTION 'Explicit retry required to renew queue time'; END IF;
        IF NOT(OLD.status='FAILED' AND NEW.status='QUEUED')
          AND NEW.correlation_id<>OLD.correlation_id
        THEN RAISE EXCEPTION 'Automatic work retains command correlation'; END IF;
        IF OLD.status IN ('QUEUED','RUNNING') AND NEW.status IN ('QUEUED','RUNNING')
          AND (NEW.grant_family IS DISTINCT FROM OLD.grant_family OR
            NEW.grant_authenticated_at IS DISTINCT FROM OLD.grant_authenticated_at)
        THEN RAISE EXCEPTION 'Automatic work cannot renew authorization'; END IF;
        IF NEW.status='READY' AND NOT export_grant_valid(NEW.request_id,OLD.grant_family,
          OLD.grant_authenticated_at,NEW.updated_at)
        THEN RAISE EXCEPTION 'Publication authorization expired'; END IF;
        IF NEW.status='EXPIRED' AND (NEW.finished_at<>OLD.finished_at OR NOT EXISTS(
          SELECT 1 FROM personal_export_generations g WHERE g.id=OLD.generation_id
            AND g.expires_at<=NEW.updated_at))
        THEN RAISE EXCEPTION 'Live export cannot expire early'; END IF;
      END IF;
      IF NEW.status IN ('QUEUED','RUNNING') AND (NOT export_grant_valid(NEW.request_id,
          NEW.grant_family,NEW.grant_authenticated_at,NEW.updated_at) OR NOT EXISTS(
          SELECT 1 FROM data_subject_requests WHERE id=NEW.request_id AND completed_at IS NULL))
      THEN RAISE EXCEPTION 'Pending owned request and current grant required'; END IF;
      IF NEW.status='RUNNING' AND NOT EXISTS(SELECT 1 FROM personal_export_generations g
        WHERE g.id=NEW.generation_id AND g.request_id=NEW.request_id
          AND g.created_at=NEW.updated_at AND g.published_at IS NULL)
      THEN RAISE EXCEPTION 'Fresh owned generation required'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_personal_export_job BEFORE INSERT OR UPDATE OR DELETE
      ON personal_export_jobs FOR EACH ROW EXECUTE FUNCTION personal_export_job_guard();

    CREATE FUNCTION personal_export_generation_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='DELETE' THEN
        IF coalesce(OLD.expires_at,OLD.lease_until)>current_timestamp
        THEN RAISE EXCEPTION 'Export generation has not expired'; END IF;
        RETURN OLD;
      END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.published_at IS NOT NULL OR NOT EXISTS(SELECT 1 FROM personal_export_jobs j
          JOIN data_subject_requests r ON r.id=j.request_id WHERE j.request_id=NEW.request_id
          AND j.status='QUEUED' AND j.attempts<3 AND r.completed_at IS NULL
          AND NEW.created_at>=j.queued_at AND export_grant_valid(j.request_id,j.grant_family,
            j.grant_authenticated_at,NEW.created_at))
        THEN RAISE EXCEPTION 'Generation requires an authorized queued request'; END IF;
      ELSE
        IF (to_jsonb(NEW)-ARRAY['published_at','expires_at','encrypted_manifest','digest','size'])
          IS DISTINCT FROM
          (to_jsonb(OLD)-ARRAY['published_at','expires_at','encrypted_manifest','digest','size'])
          OR OLD.published_at IS NOT NULL OR NEW.published_at IS NULL OR NOT EXISTS(
          SELECT 1 FROM personal_export_jobs j JOIN data_subject_requests r ON r.id=j.request_id
          WHERE j.request_id=NEW.request_id AND j.generation_id=NEW.id AND j.status='RUNNING'
            AND r.completed_at IS NULL AND export_grant_valid(j.request_id,j.grant_family,
              j.grant_authenticated_at,NEW.published_at))
        THEN RAISE EXCEPTION 'Only current authorized generation can publish once'; END IF;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_personal_export_generation BEFORE INSERT OR UPDATE OR DELETE
      ON personal_export_generations FOR EACH ROW
      EXECUTE FUNCTION personal_export_generation_guard();

    CREATE OR REPLACE FUNCTION data_request_completion_guard()
      RETURNS trigger LANGUAGE plpgsql AS $$
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
        OR NEW.retention_due_at IS NULL OR NEW.retention_due_at<>NEW.completed_at+interval '6 years'
        OR NEW.export_digest IS NULL OR NOT (
          EXISTS(SELECT 1 FROM data_exports e WHERE e.request_id=NEW.id
            AND e.created_at=NEW.completed_at AND e.digest=NEW.export_digest) OR
          EXISTS(SELECT 1 FROM personal_export_generations g WHERE g.request_id=NEW.id
            AND g.published_at=NEW.completed_at AND g.digest=NEW.export_digest))
      THEN RAISE EXCEPTION 'Invalid export completion'; END IF;
      RETURN NEW;
    END $$;
    CREATE FUNCTION personal_export_requires_completion() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.published_at IS NOT NULL AND NOT EXISTS(
        SELECT 1 FROM data_subject_requests r JOIN personal_export_jobs j ON j.request_id=r.id
        WHERE r.id=NEW.request_id AND r.completed_at=NEW.published_at AND r.export_digest=NEW.digest
          AND j.status='READY' AND j.generation_id=NEW.id AND j.finished_at=NEW.published_at)
      THEN RAISE EXCEPTION 'Private export requires atomic completion'; END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER private_export_completion AFTER UPDATE
      ON personal_export_generations DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
      EXECUTE FUNCTION personal_export_requires_completion();
    CREATE FUNCTION personal_export_ready_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.status='READY' AND NOT EXISTS(SELECT 1 FROM personal_export_generations g
        JOIN data_subject_requests r ON r.id=g.request_id WHERE g.id=NEW.generation_id
          AND g.request_id=NEW.request_id AND g.published_at=NEW.finished_at
          AND r.completed_at=g.published_at AND r.export_digest=g.digest)
      THEN RAISE EXCEPTION 'Ready job requires completed artifact'; END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER private_export_ready AFTER UPDATE ON personal_export_jobs
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION personal_export_ready_guard();
    """)


def downgrade() -> None:
    raise RuntimeError(
        "Preserve export request evidence; disable async routes and use a forward fix"
    )
