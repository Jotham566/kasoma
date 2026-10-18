"""Forward fix: held receipt no-op comparison supports existing JSON menu fields."""

from alembic import op

revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION protect_channel_receipt_hold() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' THEN
        IF NEW.id IS DISTINCT FROM OLD.id
        THEN RAISE EXCEPTION 'Channel receipt identity is immutable'; END IF;
      END IF;
      IF NOT record_is_held(TG_ARGV[0],OLD.id,clock_timestamp()) THEN
        IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
      END IF;
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      IF to_jsonb(NEW) IS NOT DISTINCT FROM to_jsonb(OLD) THEN RETURN NEW; END IF;
      IF TG_ARGV[0]='CHANNEL_INBOUND_RECEIPT' THEN
        RAISE EXCEPTION 'Terminal channel receipt is legally held';
      END IF;
      IF (to_jsonb(NEW)-ARRAY['status','status_at','error_code']) IS DISTINCT FROM
         (to_jsonb(OLD)-ARRAY['status','status_at','error_code'])
        OR NEW.status_at IS NULL
        OR (OLD.status_at IS NOT NULL AND NEW.status_at<OLD.status_at)
      THEN RAISE EXCEPTION 'Terminal channel receipt is legally held'; END IF;
      IF (NEW.status=OLD.status AND NEW.error_code IS NOT DISTINCT FROM OLD.error_code)
        OR (OLD.status='SENT' AND NEW.status IN ('DELIVERED','READ')
            AND NEW.error_code IS NOT DISTINCT FROM OLD.error_code)
        OR (OLD.status='DELIVERED' AND NEW.status='READ'
            AND NEW.error_code IS NOT DISTINCT FROM OLD.error_code)
        OR (OLD.status='SENT' AND NEW.status='FAILED' AND NEW.error_code='PROVIDER_FAILED')
      THEN RETURN NEW; END IF;
      RAISE EXCEPTION 'Terminal channel receipt is legally held';
    END $$;
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve working JSON receipt guards and apply a forward fix")
