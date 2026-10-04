"""FR-WA-002–006: bounded conversation pointers and minimized reply references."""

from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION channel_attempt_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM session_items si
        JOIN assessment_sessions s ON s.id=si.session_id
        JOIN item_versions v ON v.id=si.item_version_id
        WHERE si.id=NEW.session_item_id
          AND (v.document->'channel_suitability')::jsonb ? NEW.channel
          AND (NEW.channel='WEB' OR (s.kind='REVISION' AND s.item_count=5)))
      THEN RAISE EXCEPTION 'Unsupported channel assignment'; END IF;
      RETURN NEW;
    END $$;
    ALTER TABLE inbound_messages ADD COLUMN reply_reference text;
    ALTER TABLE inbound_messages ADD COLUMN reply_encrypted text;
    ALTER TABLE inbound_messages DROP CONSTRAINT inbound_messages_command_check;
    ALTER TABLE inbound_messages ADD CONSTRAINT inbound_messages_command_check
      CHECK(command IN
        ('LINK','STOP','HELP','UNSUPPORTED','STATUS','START','CONTINUE','PROGRESS','ANSWER'));
    ALTER TABLE inbound_messages ADD CONSTRAINT transient_reply CHECK(
      (reply_reference IS NULL OR length(reply_reference)<=256)
      AND (reply_encrypted IS NULL OR (status='QUEUED' AND command='ANSWER'
        AND reply_reference IS NOT NULL AND length(reply_encrypted)<=1024)));
    ALTER TABLE outbound_messages ADD COLUMN link_revision int;
    ALTER TABLE outbound_messages ADD COLUMN session_item_id uuid REFERENCES session_items(id);
    ALTER TABLE outbound_messages ADD COLUMN attempt_id uuid REFERENCES attempts(id);
    ALTER TABLE outbound_messages ADD COLUMN menu_topic_ids json;
    ALTER TABLE outbound_messages DROP CONSTRAINT outbound_messages_template_check;
    ALTER TABLE outbound_messages ADD CONSTRAINT outbound_messages_template_check
      CHECK(template IN ('LINKED','STOPPED','HELP','LINK_REJECTED','UNSUPPORTED',
        'PRACTICE_MENU','PRACTICE_QUESTION','PRACTICE_FEEDBACK','PRACTICE_NOTICE','PROGRESS'));
    ALTER TABLE outbound_messages ADD CONSTRAINT bound_practice_reply CHECK(
      template NOT IN
        ('PRACTICE_MENU','PRACTICE_QUESTION','PRACTICE_FEEDBACK','PRACTICE_NOTICE','PROGRESS')
      OR (link_id IS NOT NULL AND actor_id IS NOT NULL AND link_revision IS NOT NULL AND
        link_revision>0));
    ALTER TABLE outbound_messages ADD CONSTRAINT practice_reply_shape CHECK(
      (template='PRACTICE_MENU' AND menu_topic_ids IS NOT NULL
        AND json_typeof(menu_topic_ids)='array' AND json_array_length(menu_topic_ids) BETWEEN
        1 AND 6
        AND session_item_id IS NULL AND attempt_id IS NULL)
      OR (template='PRACTICE_QUESTION' AND session_item_id IS NOT NULL AND attempt_id IS NULL
        AND menu_topic_ids IS NULL)
      OR (template='PRACTICE_FEEDBACK' AND attempt_id IS NOT NULL AND session_item_id IS NOT
        NULL AND menu_topic_ids IS NULL)
      OR (template NOT IN ('PRACTICE_MENU','PRACTICE_QUESTION','PRACTICE_FEEDBACK')
        AND session_item_id IS NULL AND attempt_id IS NULL AND menu_topic_ids IS NULL));
    CREATE TABLE conversation_states (
      link_id uuid PRIMARY KEY REFERENCES channel_links(id), actor_id uuid NOT NULL REFERENCES
        users(id),
      link_revision int NOT NULL CHECK(link_revision>0),
      session_id uuid REFERENCES assessment_sessions(id),
      expected_outbound_id uuid REFERENCES outbound_messages(id) ON DELETE CASCADE,
      updated_at timestamptz NOT NULL CHECK(isfinite(updated_at)),
      expires_at timestamptz NOT NULL CHECK(expires_at=updated_at+interval '24 hours'));
    CREATE INDEX conversation_expiry ON conversation_states(expires_at);
    CREATE FUNCTION conversation_owner_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM channel_links l WHERE l.id=NEW.link_id
        AND l.user_id=NEW.actor_id AND l.revision=NEW.link_revision AND l.status='ACTIVE')
        OR (NEW.session_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM assessment_sessions s
          WHERE s.id=NEW.session_id AND s.learner_id=NEW.actor_id AND s.kind='REVISION' AND
        s.item_count=5))
      THEN RAISE EXCEPTION 'Invalid conversation ownership'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_conversation BEFORE INSERT OR UPDATE ON conversation_states
      FOR EACH ROW EXECUTE FUNCTION conversation_owner_guard();
    """)


def downgrade() -> None:
    raise RuntimeError(
        "Preserve channel and learning evidence; disable entry points and forward fix"
    )
