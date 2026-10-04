"""FR-WA-002/003: preserve immutable evidence while admitting supported channel attempts."""

from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE attempts DROP CONSTRAINT attempts_channel_check;
    ALTER TABLE attempts ADD CONSTRAINT attempts_channel_check
      CHECK(channel IN ('WEB','WHATSAPP'));
    CREATE FUNCTION channel_attempt_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.channel='WHATSAPP' AND NOT EXISTS(
        SELECT 1 FROM session_items si JOIN assessment_sessions s ON s.id=si.session_id
        JOIN item_versions v ON v.id=si.item_version_id
        WHERE si.id=NEW.session_item_id AND s.kind='REVISION' AND s.item_count=5
          AND (v.document->'channel_suitability')::jsonb ? 'WHATSAPP'
      ) THEN RAISE EXCEPTION 'Unsupported channel assignment'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER supported_channel_attempt BEFORE INSERT ON attempts
      FOR EACH ROW EXECUTE FUNCTION channel_attempt_guard();
    """)


def downgrade() -> None:
    raise RuntimeError("Retain immutable channel evidence and use a forward fix")
