"""Exact minimized terminal receipts; live channel capability retention is unchanged."""

from alembic import op

revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE legal_holds DROP CONSTRAINT legal_holds_record_type_check;
    ALTER TABLE legal_holds ADD CONSTRAINT legal_holds_record_type_check
      CHECK(record_type IN ('CONSENT','ATTEMPT','CONTENT_FLAG','DATA_REQUEST',
        'GRADE','MASTERY_EVIDENCE','MASTERY_HISTORY','FLAG_HISTORY','DATA_REQUEST_REVIEW',
        'GRADING_HISTORY','GRADING_PUBLICATION','GRADING_AUDIT','GRADING_REVIEW',
        'CHANNEL_INBOUND_RECEIPT','CHANNEL_OUTBOUND_RECEIPT'));
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

    CREATE FUNCTION protect_channel_receipt_hold() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' THEN
        IF NEW.id IS DISTINCT FROM OLD.id
        THEN RAISE EXCEPTION 'Channel receipt identity is immutable'; END IF;
      END IF;
      IF NOT record_is_held(TG_ARGV[0],OLD.id,clock_timestamp()) THEN
        IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
      END IF;
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      IF NEW IS NOT DISTINCT FROM OLD THEN RETURN NEW; END IF;
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
    for table, kind in [
        ("inbound_messages", "CHANNEL_INBOUND_RECEIPT"),
        ("outbound_messages", "CHANNEL_OUTBOUND_RECEIPT"),
    ]:
        op.execute(f"""CREATE TRIGGER aa_protect_channel_receipt_hold
          BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW
          EXECUTE FUNCTION protect_channel_receipt_hold('{kind}')""")


def downgrade() -> None:
    raise RuntimeError("Preserve registered receipt holds and apply a forward fix")
