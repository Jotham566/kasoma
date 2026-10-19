"""ADR-057 synthetic minimized snapshots; operational STOP/expiry remain independent."""

from alembic import op

revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE SEQUENCE channel_conversation_versions AS bigint NO CYCLE;
    ALTER TABLE conversation_states ADD COLUMN state_version bigint NOT NULL
      DEFAULT nextval('channel_conversation_versions');
    ALTER TABLE conversation_states ALTER COLUMN state_version DROP DEFAULT;
    ALTER SEQUENCE channel_conversation_versions OWNED BY conversation_states.state_version;
    CREATE FUNCTION assign_conversation_version() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      NEW.state_version := nextval('channel_conversation_versions');
      RETURN NEW;
    END $$;
    CREATE TRIGGER conversation_version BEFORE INSERT OR UPDATE ON conversation_states
      FOR EACH ROW EXECUTE FUNCTION assign_conversation_version();

    CREATE TABLE channel_preservation_snapshots (
      id uuid PRIMARY KEY, request_id uuid NOT NULL REFERENCES data_subject_requests(id),
      source_kind text NOT NULL CHECK(source_kind IN
        ('CHANNEL_LINK_SNAPSHOT','CHANNEL_CONVERSATION_SNAPSHOT')),
      source_link_id uuid NOT NULL, link_revision integer NOT NULL CHECK(link_revision>0),
      source_state_version bigint,
      source_version text NOT NULL CHECK(source_version ~ '^[a-f0-9]{64}$'
        AND length(source_version)=64),
      captured_by uuid NOT NULL REFERENCES users(id),
      captured_at timestamptz NOT NULL CHECK(isfinite(captured_at)),
      CHECK((source_kind='CHANNEL_LINK_SNAPSHOT' AND source_state_version IS NULL)
        OR (source_kind='CHANNEL_CONVERSATION_SNAPSHOT'
          AND source_state_version IS NOT NULL AND source_state_version>0)));
    CREATE INDEX channel_snapshot_request ON channel_preservation_snapshots(request_id,id);
    CREATE TABLE channel_preservation_bodies (
      snapshot_id uuid PRIMARY KEY REFERENCES channel_preservation_snapshots(id),
      encrypted_payload text NOT NULL CHECK(length(encrypted_payload) BETWEEN 100 AND 4096
        AND encrypted_payload ~ '^[A-Za-z0-9_-]+=*$'));
    CREATE TABLE channel_preservation_disposals (
      snapshot_id uuid PRIMARY KEY REFERENCES channel_preservation_snapshots(id),
      disposed_at timestamptz NOT NULL CHECK(isfinite(disposed_at)));

    CREATE FUNCTION channel_snapshot_capture_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE request_owner uuid; source_owner uuid;
    BEGIN
      SELECT r.user_id INTO request_owner FROM data_subject_requests r
        JOIN data_request_reviews v ON v.request_id=r.id
        WHERE r.id=NEW.request_id AND r.kind='DELETE' AND r.completed_at IS NULL
          AND v.actor_id=NEW.captured_by AND r.user_id<>NEW.captured_by
          AND v.created_at<=NEW.captured_at
        FOR UPDATE OF r;
      IF request_owner IS NULL OR NEW.captured_at>clock_timestamp()
        OR NOT EXISTS(SELECT 1 FROM user_roles
          WHERE user_id=NEW.captured_by AND role='ADMIN')
      THEN RAISE EXCEPTION 'Independent current snapshot claimant required'; END IF;
      SELECT l.user_id INTO source_owner FROM channel_links l
        JOIN channel_senders s ON s.sender_hash=l.sender_hash
        WHERE l.id=NEW.source_link_id AND l.revision=NEW.link_revision
          AND l.user_id=request_owner AND l.status='ACTIVE'
          AND (s.barrier_at IS NULL OR s.barrier_at<l.linked_at)
        FOR UPDATE OF l,s;
      IF source_owner IS DISTINCT FROM request_owner
      THEN RAISE EXCEPTION 'Exact available owned channel source required'; END IF;
      IF NEW.source_kind='CHANNEL_CONVERSATION_SNAPSHOT' AND NOT EXISTS(
        SELECT 1 FROM conversation_states c WHERE c.link_id=NEW.source_link_id
          AND c.actor_id=request_owner AND c.link_revision=NEW.link_revision
          AND c.state_version=NEW.source_state_version AND c.expires_at>clock_timestamp()
          AND (c.session_id IS NOT NULL OR c.expected_outbound_id IS NOT NULL)
          AND (c.expected_outbound_id IS NULL OR EXISTS(
            SELECT 1 FROM outbound_messages o WHERE o.id=c.expected_outbound_id
              AND o.actor_id=request_owner AND o.link_id=NEW.source_link_id
              AND o.link_revision=NEW.link_revision FOR UPDATE))
        FOR UPDATE)
      THEN RAISE EXCEPTION 'Exact available owned conversation version required'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER channel_snapshot_capture BEFORE INSERT ON channel_preservation_snapshots
      FOR EACH ROW EXECUTE FUNCTION channel_snapshot_capture_guard();
    CREATE TRIGGER immutable_channel_snapshot BEFORE UPDATE OR DELETE
      ON channel_preservation_snapshots FOR EACH ROW EXECUTE FUNCTION assessment_immutable();

    CREATE FUNCTION channel_snapshot_body_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE kind text;
    BEGIN
      IF TG_OP='UPDATE' THEN RAISE EXCEPTION 'Snapshot ciphertext is immutable'; END IF;
      IF TG_OP='INSERT' THEN
        IF EXISTS(SELECT 1 FROM channel_preservation_disposals
          WHERE snapshot_id=NEW.snapshot_id)
        THEN RAISE EXCEPTION 'Disposed snapshot cannot be recreated'; END IF;
        RETURN NEW;
      END IF;
      SELECT source_kind INTO kind FROM channel_preservation_snapshots
        WHERE id=OLD.snapshot_id;
      IF record_is_held(kind,OLD.snapshot_id,clock_timestamp())
      THEN RAISE EXCEPTION 'Snapshot evidence is actively preserved'; END IF;
      INSERT INTO channel_preservation_disposals(snapshot_id,disposed_at)
        VALUES(OLD.snapshot_id,clock_timestamp());
      RETURN OLD;
    END $$;
    CREATE TRIGGER channel_snapshot_body BEFORE INSERT OR UPDATE OR DELETE
      ON channel_preservation_bodies FOR EACH ROW EXECUTE FUNCTION channel_snapshot_body_guard();
    CREATE TRIGGER immutable_channel_disposal BEFORE UPDATE OR DELETE
      ON channel_preservation_disposals FOR EACH ROW EXECUTE FUNCTION assessment_immutable();

    CREATE FUNCTION channel_snapshot_complete() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NOT EXISTS(SELECT 1 FROM channel_preservation_bodies WHERE snapshot_id=NEW.id)
        OR NOT record_is_held(NEW.source_kind,NEW.id,clock_timestamp())
      THEN
        RAISE EXCEPTION 'Snapshot capture requires encrypted evidence and finite decision';
      END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER channel_snapshot_complete AFTER INSERT
      ON channel_preservation_snapshots DEFERRABLE INITIALLY DEFERRED
      FOR EACH ROW EXECUTE FUNCTION channel_snapshot_complete();
    CREATE FUNCTION channel_snapshot_disposal_complete() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF EXISTS(SELECT 1 FROM channel_preservation_bodies WHERE snapshot_id=NEW.snapshot_id)
      THEN RAISE EXCEPTION 'Snapshot disposal requires evidence removal'; END IF;
      RETURN NULL;
    END $$;
    CREATE CONSTRAINT TRIGGER channel_snapshot_disposal_complete AFTER INSERT
      ON channel_preservation_disposals DEFERRABLE INITIALLY DEFERRED
      FOR EACH ROW EXECUTE FUNCTION channel_snapshot_disposal_complete();

    ALTER TABLE legal_holds DROP CONSTRAINT legal_holds_record_type_check;
    ALTER TABLE legal_holds ADD CONSTRAINT legal_holds_record_type_check
      CHECK(record_type IN ('CONSENT','ATTEMPT','CONTENT_FLAG','DATA_REQUEST',
        'GRADE','MASTERY_EVIDENCE','MASTERY_HISTORY','FLAG_HISTORY','DATA_REQUEST_REVIEW',
        'GRADING_HISTORY','GRADING_PUBLICATION','GRADING_AUDIT','GRADING_REVIEW',
        'CHANNEL_INBOUND_RECEIPT','CHANNEL_OUTBOUND_RECEIPT',
        'CHANNEL_LINK_SNAPSHOT','CHANNEL_CONVERSATION_SNAPSHOT'));
    """)
    op.execute("""
    CREATE OR REPLACE FUNCTION legal_hold_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE owner_id uuid; request_owner uuid; actor uuid;
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Hold evidence is retained'; END IF;
      actor := CASE WHEN TG_OP='INSERT' THEN NEW.created_by ELSE NEW.released_by END;
      SELECT r.user_id INTO request_owner FROM data_subject_requests r
        JOIN data_request_reviews v ON v.request_id=r.id
        WHERE r.id=NEW.request_id AND r.kind='DELETE' AND r.completed_at IS NULL
          AND v.actor_id=actor AND r.user_id<>actor;
      IF request_owner IS NULL OR NOT EXISTS(SELECT 1 FROM user_roles
        WHERE user_id=actor AND role='ADMIN')
      THEN RAISE EXCEPTION 'Independent request claimant required'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.released_at IS NOT NULL OR NEW.released_by IS NOT NULL
          OR NEW.release_reference IS NOT NULL
        THEN RAISE EXCEPTION 'New hold must be unreleased'; END IF;
        CASE NEW.record_type
          WHEN 'CONSENT' THEN SELECT user_id INTO owner_id FROM consent_records
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'ATTEMPT' THEN SELECT learner_id INTO owner_id FROM attempts
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'GRADE' THEN SELECT a.learner_id INTO owner_id FROM grades g
            JOIN attempts a ON a.id=g.attempt_id WHERE g.attempt_id=NEW.record_id
            FOR KEY SHARE OF g,a;
          WHEN 'MASTERY_EVIDENCE' THEN SELECT learner_id INTO owner_id FROM mastery_evidence
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'MASTERY_HISTORY' THEN SELECT e.learner_id INTO owner_id
            FROM mastery_estimate_history h JOIN mastery_evidence e ON e.id=h.evidence_id
            WHERE h.id=NEW.record_id FOR KEY SHARE OF h,e;
          WHEN 'GRADING_REVIEW' THEN SELECT a.learner_id INTO owner_id
            FROM grading_audit_reviews r JOIN grading_audit_assignments g ON g.id=r.id
            JOIN attempts a ON a.id=g.attempt_id
            WHERE r.id=NEW.record_id FOR KEY SHARE OF r,g,a;
          WHEN 'GRADING_PUBLICATION' THEN SELECT a.learner_id INTO owner_id
            FROM grading_publications p JOIN attempts a ON a.id=p.attempt_id
            WHERE p.attempt_id=NEW.record_id FOR KEY SHARE OF p,a;
          WHEN 'GRADING_AUDIT' THEN SELECT a.learner_id INTO owner_id
            FROM grading_audit_assignments g JOIN attempts a ON a.id=g.attempt_id
            WHERE g.id=NEW.record_id FOR KEY SHARE OF g,a;
          WHEN 'GRADING_HISTORY' THEN SELECT a.learner_id INTO owner_id
            FROM assessment_grading_history h JOIN attempts a ON a.id=h.attempt_id
            WHERE h.id=NEW.record_id FOR KEY SHARE OF h,a;
          WHEN 'FLAG_HISTORY' THEN SELECT f.reporter_id INTO owner_id
            FROM content_flag_history h JOIN content_flags f ON f.id=h.flag_id
            WHERE h.id=NEW.record_id FOR KEY SHARE OF h,f;
          WHEN 'DATA_REQUEST_REVIEW' THEN SELECT r.user_id INTO owner_id
            FROM data_request_reviews v JOIN data_subject_requests r ON r.id=v.request_id
            WHERE v.request_id=NEW.record_id FOR KEY SHARE OF v,r;
          WHEN 'CONTENT_FLAG' THEN SELECT reporter_id INTO owner_id FROM content_flags
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'DATA_REQUEST' THEN SELECT user_id INTO owner_id FROM data_subject_requests
            WHERE id=NEW.record_id FOR KEY SHARE;
          WHEN 'CHANNEL_INBOUND_RECEIPT' THEN SELECT actor_id INTO owner_id
            FROM inbound_messages WHERE id=NEW.record_id AND status<>'QUEUED'
              AND processed_at IS NOT NULL AND sender_encrypted IS NULL
              AND code_hash IS NULL AND reply_encrypted IS NULL
              AND NEW.created_at<=clock_timestamp() FOR UPDATE;
          WHEN 'CHANNEL_OUTBOUND_RECEIPT' THEN SELECT actor_id INTO owner_id
            FROM outbound_messages WHERE id=NEW.record_id AND status<>'PENDING'
              AND recipient_encrypted IS NULL
              AND NEW.created_at<=clock_timestamp() FOR UPDATE;
          WHEN 'CHANNEL_LINK_SNAPSHOT','CHANNEL_CONVERSATION_SNAPSHOT' THEN
            SELECT r.user_id INTO owner_id FROM channel_preservation_snapshots s
              JOIN channel_preservation_bodies b ON b.snapshot_id=s.id
              JOIN data_subject_requests r ON r.id=s.request_id
              WHERE s.id=NEW.record_id AND s.source_kind=NEW.record_type
                AND s.request_id=NEW.request_id AND NEW.created_at<=clock_timestamp()
                AND NEW.expires_at>clock_timestamp() FOR UPDATE OF b;
          ELSE RAISE EXCEPTION 'Unsupported hold record';
        END CASE;
        IF owner_id IS DISTINCT FROM request_owner
          OR NOT EXISTS(SELECT 1 FROM data_request_reviews
            WHERE request_id=NEW.request_id AND created_at<=NEW.created_at)
        THEN RAISE EXCEPTION 'Hold target must belong to requester'; END IF;
      ELSE
        IF (to_jsonb(NEW)-ARRAY['released_at','released_by','release_reference']) IS DISTINCT FROM
           (to_jsonb(OLD)-ARRAY['released_at','released_by','release_reference'])
          OR OLD.released_at IS NOT NULL OR NEW.released_at IS NULL
        THEN RAISE EXCEPTION 'Only one hold release is permitted'; END IF;
      END IF;
      RETURN NEW;
    END $$;
    """)


def downgrade() -> None:
    raise RuntimeError(
        "Disable capture; preserve snapshot readers/evidence and apply a forward fix"
    )
