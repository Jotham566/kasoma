"""ADR-060 forward correction: claim actor is not the EXPORT subject owner."""

from alembic import op

revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION legal_hold_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE owner_id uuid; request_owner uuid; actor uuid; source_request uuid;
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
          WHEN 'DATA_REQUEST_RECEIPT','EXPORT_JOB_RECEIPT' THEN
            IF NEW.record_type='DATA_REQUEST_RECEIPT' THEN
              SELECT request_id INTO source_request FROM data_request_receipts
                WHERE id=NEW.record_id;
            ELSE source_request := NEW.record_id; END IF;
            SELECT user_id INTO owner_id FROM data_subject_requests
              WHERE id=source_request AND kind='EXPORT' FOR UPDATE;
            IF owner_id IS NOT NULL THEN
              IF NEW.record_type='DATA_REQUEST_RECEIPT' THEN
                PERFORM 1 FROM data_request_receipts WHERE id=NEW.record_id
                  AND request_id=source_request FOR UPDATE;
              ELSE
                PERFORM 1 FROM personal_export_jobs j WHERE request_id=source_request
                  AND status='EXPIRED' AND grant_family IS NULL
                  AND grant_authenticated_at IS NULL AND generation_id IS NULL
                  AND NOT EXISTS(SELECT 1 FROM personal_export_generations g
                    WHERE g.request_id=j.request_id) FOR UPDATE;
              END IF;
              IF NOT FOUND THEN owner_id := NULL; END IF;
            END IF;
            IF NEW.created_at>clock_timestamp() OR NEW.expires_at<=clock_timestamp()
            THEN owner_id := NULL; END IF;
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
    raise RuntimeError("Preserve receipt subject ownership and use a forward fix")
