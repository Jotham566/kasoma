"""FR-WA-001/004/006: additive channel linking and durable local transport state."""

from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE link_codes (
      id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users(id), key uuid NOT NULL,
      code_hash text UNIQUE, created_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
      consumed_at timestamptz, revoked_at timestamptz, UNIQUE(user_id,key),
      CHECK(isfinite(created_at) AND expires_at=created_at+interval '5 minutes'),
      CHECK(consumed_at IS NULL OR (consumed_at>=created_at
        AND consumed_at<expires_at AND isfinite(consumed_at))),
      CHECK(revoked_at IS NULL OR (revoked_at>=created_at AND isfinite(revoked_at))),
      CHECK((consumed_at IS NULL AND revoked_at IS NULL) OR code_hash IS NULL));
    CREATE INDEX link_code_expiry ON link_codes(expires_at);
    CREATE TABLE channel_senders (
      sender_hash text PRIMARY KEY, barrier_at timestamptz, last_provider_at timestamptz,
      updated_at timestamptz NOT NULL CHECK(isfinite(updated_at)),
      CHECK(barrier_at IS NULL OR isfinite(barrier_at)),
      CHECK(last_provider_at IS NULL OR isfinite(last_provider_at)));
    CREATE TABLE channel_links (
      id uuid PRIMARY KEY, user_id uuid NOT NULL UNIQUE REFERENCES users(id),
      sender_hash text NOT NULL REFERENCES channel_senders(sender_hash),
      external_identifier_encrypted text, status text NOT NULL,
      revision int NOT NULL CHECK(revision>0),
      linked_at timestamptz NOT NULL CHECK(isfinite(linked_at)),
      opted_out_at timestamptz, updated_at timestamptz NOT NULL CHECK(isfinite(updated_at)),
      CHECK(status IN ('ACTIVE','STOPPED','UNLINKED')),
      CHECK((status='ACTIVE' AND opted_out_at IS NULL AND external_identifier_encrypted IS NOT NULL)
        OR (status='STOPPED' AND opted_out_at IS NOT NULL
          AND external_identifier_encrypted IS NOT NULL)
        OR (status='UNLINKED' AND opted_out_at IS NOT NULL
          AND external_identifier_encrypted IS NULL)),
      CHECK(opted_out_at IS NULL OR (opted_out_at>=linked_at AND isfinite(opted_out_at))));
    CREATE UNIQUE INDEX one_bound_whatsapp_sender ON channel_links(sender_hash)
      WHERE status IN ('ACTIVE','STOPPED');
    CREATE TABLE inbound_messages (
      id uuid PRIMARY KEY, message_hash text NOT NULL UNIQUE, request_hash text NOT NULL,
      request_id uuid NOT NULL, sender_hash text NOT NULL, sender_encrypted text,
      actor_id uuid REFERENCES users(id), command text NOT NULL,
      code_hash text, status_reference text, delivery_status text,
      provider_at timestamptz NOT NULL CHECK(isfinite(provider_at)),
      received_at timestamptz NOT NULL CHECK(isfinite(received_at)),
      available_at timestamptz NOT NULL CHECK(isfinite(available_at)), processed_at timestamptz,
      status text NOT NULL CHECK(status IN ('QUEUED','PROCESSED','REJECTED','FAILED')),
      attempts int NOT NULL CHECK(attempts BETWEEN 0 AND 3), error_code text,
      CHECK(command IN ('LINK','STOP','HELP','UNSUPPORTED','STATUS')),
      CHECK((status='QUEUED' AND processed_at IS NULL AND attempts<3)
        OR (status<>'QUEUED' AND processed_at IS NOT NULL AND isfinite(processed_at)
          AND sender_encrypted IS NULL AND code_hash IS NULL)));
    CREATE INDEX inbound_due ON inbound_messages(available_at) WHERE status='QUEUED';
    CREATE INDEX inbound_actor ON inbound_messages(actor_id,received_at);
    CREATE TABLE outbound_messages (
      id uuid PRIMARY KEY, inbound_id uuid NOT NULL UNIQUE REFERENCES inbound_messages(id),
      link_id uuid REFERENCES channel_links(id), actor_id uuid REFERENCES users(id),
      recipient_hash text NOT NULL, recipient_encrypted text, template text NOT NULL,
      status text NOT NULL, provider_id text UNIQUE,
      attempts int NOT NULL CHECK(attempts BETWEEN 0 AND 3),
      error_code text, created_at timestamptz NOT NULL CHECK(isfinite(created_at)),
      available_at timestamptz NOT NULL CHECK(isfinite(available_at)), sent_at timestamptz,
      status_at timestamptz,
      CHECK(template IN ('LINKED','STOPPED','HELP','LINK_REJECTED','UNSUPPORTED')),
      CHECK(status IN ('PENDING','SENT','DELIVERED','READ','CANCELLED','FAILED')),
      CHECK((status='PENDING' AND recipient_encrypted IS NOT NULL AND attempts<3)
        OR (status<>'PENDING' AND recipient_encrypted IS NULL)),
      CHECK(status NOT IN ('SENT','DELIVERED','READ') OR
        (provider_id IS NOT NULL AND sent_at IS NOT NULL AND isfinite(sent_at))),
      CHECK(status_at IS NULL OR isfinite(status_at)));
    CREATE INDEX outbound_due ON outbound_messages(available_at) WHERE status='PENDING';
    CREATE INDEX outbound_actor ON outbound_messages(actor_id,created_at);
    CREATE TABLE channel_mutation_receipts (
      actor_id uuid NOT NULL REFERENCES users(id), key uuid NOT NULL, request_hash text NOT NULL,
      created_at timestamptz NOT NULL CHECK(isfinite(created_at)), PRIMARY KEY(actor_id,key));
    CREATE FUNCTION protect_link_code() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF (NEW.id,NEW.user_id,NEW.key,NEW.created_at,NEW.expires_at) IS DISTINCT FROM
         (OLD.id,OLD.user_id,OLD.key,OLD.created_at,OLD.expires_at)
        OR (NEW.code_hash IS NOT NULL AND NEW.code_hash IS DISTINCT FROM OLD.code_hash)
        OR (OLD.consumed_at IS NOT NULL AND NEW.consumed_at IS DISTINCT FROM OLD.consumed_at)
        OR (OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS DISTINCT FROM OLD.revoked_at)
        OR (OLD.consumed_at IS NULL AND NEW.consumed_at IS NOT NULL AND
          (OLD.code_hash IS NULL OR OLD.revoked_at IS NOT NULL))
      THEN RAISE EXCEPTION 'Invalid one-time code transition'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER link_code_guard BEFORE UPDATE ON link_codes
      FOR EACH ROW EXECUTE FUNCTION protect_link_code();
    CREATE FUNCTION protect_channel_owner() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF (NEW.id,NEW.user_id) IS DISTINCT FROM (OLD.id,OLD.user_id)
        OR (OLD.status<>'UNLINKED' AND NEW.sender_hash<>OLD.sender_hash)
        OR NEW.linked_at<OLD.linked_at OR NEW.updated_at<OLD.updated_at
        OR NEW.revision<>OLD.revision+1
      THEN RAISE EXCEPTION 'Invalid channel ownership transition'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER channel_owner_guard BEFORE UPDATE ON channel_links
      FOR EACH ROW EXECUTE FUNCTION protect_channel_owner();
    """)


def downgrade() -> None:
    raise RuntimeError(
        "Disable channel entry points/workers; preserve evidence and apply a forward fix"
    )
