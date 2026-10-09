"""FR-ID-006/BR-010: exact immutable flag-history and request-review holds."""

from alembic import op

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE legal_holds DROP CONSTRAINT legal_holds_record_type_check;
    ALTER TABLE legal_holds ADD CONSTRAINT legal_holds_record_type_check
      CHECK(record_type IN ('CONSENT','ATTEMPT','CONTENT_FLAG','DATA_REQUEST',
        'GRADE','MASTERY_EVIDENCE','MASTERY_HISTORY','FLAG_HISTORY','DATA_REQUEST_REVIEW'));
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
    CREATE FUNCTION protect_held_request_review() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF record_is_held('DATA_REQUEST_REVIEW',OLD.request_id,current_timestamp)
      THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      RETURN OLD;
    END $$;
    CREATE TRIGGER aa_protect_held_record BEFORE DELETE ON data_request_reviews
      FOR EACH ROW EXECUTE FUNCTION protect_held_request_review();
    CREATE TRIGGER aa_protect_held_record BEFORE DELETE ON content_flag_history
      FOR EACH ROW EXECUTE FUNCTION protect_held_record('FLAG_HISTORY');
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve accountability holds; disable routes and use a forward fix")
