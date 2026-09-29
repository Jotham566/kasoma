"""FR-ID-006: non-destructive, auditable data request intake and review."""

from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE data_subject_requests (
      id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users(id),
      kind text NOT NULL CHECK(kind IN ('EXPORT','DELETE')),
      authenticated_at timestamptz NOT NULL,
      verification_method text NOT NULL CHECK(verification_method='RECENT_OTP'),
      retention_policy text NOT NULL CHECK(retention_policy='SIX_YEARS_AFTER_COMPLETION'),
      created_at timestamptz NOT NULL, UNIQUE(user_id,kind),
      CHECK(authenticated_at<=created_at AND authenticated_at>created_at-interval '10 minutes'));
    CREATE INDEX data_requests_user ON data_subject_requests(user_id,id);
    CREATE TABLE data_request_reviews (
      request_id uuid PRIMARY KEY REFERENCES data_subject_requests(id),
      actor_id uuid NOT NULL REFERENCES users(id), created_at timestamptz NOT NULL);
    CREATE TABLE data_request_receipts (
      actor_id uuid NOT NULL REFERENCES users(id), key uuid NOT NULL,
      request_hash text NOT NULL, request_id uuid NOT NULL REFERENCES data_subject_requests(id),
      PRIMARY KEY(actor_id,key));
    CREATE FUNCTION data_request_review_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM user_roles WHERE user_id=NEW.actor_id AND role='ADMIN')
        OR NOT EXISTS(SELECT 1 FROM data_subject_requests
          WHERE id=NEW.request_id AND created_at<=NEW.created_at AND user_id<>NEW.actor_id)
      THEN RAISE EXCEPTION 'Independent administrator required'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_data_review BEFORE INSERT ON data_request_reviews
      FOR EACH ROW EXECUTE FUNCTION data_request_review_guard();
    """)
    for table in ["data_subject_requests", "data_request_reviews", "data_request_receipts"]:
        op.execute(
            f"CREATE TRIGGER immutable_data_request BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION assessment_immutable()"
        )


def downgrade() -> None:
    raise RuntimeError("Preserve request evidence; use a retention-aware forward migration")
