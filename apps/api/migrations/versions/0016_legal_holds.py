"""FR-ID-006: finite, owned-record holds; no deletion processor or evidence rewrite."""

from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE legal_holds (
      id uuid PRIMARY KEY, request_id uuid NOT NULL REFERENCES data_subject_requests(id),
      record_type text NOT NULL
        CHECK(record_type IN ('CONSENT','ATTEMPT','CONTENT_FLAG','DATA_REQUEST')),
      record_id uuid NOT NULL, decision_reference uuid NOT NULL,
      reason text NOT NULL CHECK(reason IN ('LEGAL_OBLIGATION','SECURITY_INVESTIGATION')),
      created_by uuid NOT NULL REFERENCES users(id), created_at timestamptz NOT NULL,
      expires_at timestamptz NOT NULL,
      released_at timestamptz, released_by uuid REFERENCES users(id), release_reference uuid,
      CHECK(isfinite(created_at) AND isfinite(expires_at) AND expires_at>created_at),
      CHECK((released_at IS NULL AND released_by IS NULL AND release_reference IS NULL)
        OR (released_at IS NOT NULL AND released_by IS NOT NULL AND release_reference IS NOT NULL
            AND isfinite(released_at) AND released_at>=created_at AND released_at<expires_at)));
    CREATE INDEX legal_holds_request ON legal_holds(request_id,id);
    CREATE INDEX legal_holds_record ON legal_holds(record_type,record_id,expires_at)
      WHERE released_at IS NULL;
    CREATE TABLE legal_hold_receipts (
      actor_id uuid NOT NULL REFERENCES users(id), key uuid NOT NULL, request_hash text NOT NULL,
      hold_id uuid NOT NULL REFERENCES legal_holds(id), PRIMARY KEY(actor_id,key));
    CREATE TRIGGER immutable_hold_receipt BEFORE UPDATE OR DELETE ON legal_hold_receipts
      FOR EACH ROW EXECUTE FUNCTION assessment_immutable();
    CREATE FUNCTION legal_hold_guard() RETURNS trigger LANGUAGE plpgsql AS $$
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
    CREATE TRIGGER protect_legal_hold BEFORE INSERT OR UPDATE OR DELETE ON legal_holds
      FOR EACH ROW EXECUTE FUNCTION legal_hold_guard();
    CREATE FUNCTION record_is_held(kind text, target uuid, at_time timestamptz)
      RETURNS boolean LANGUAGE sql STABLE AS $$
      SELECT EXISTS(SELECT 1 FROM legal_holds WHERE record_type=kind AND record_id=target
        AND released_at IS NULL AND created_at<=at_time AND expires_at>at_time)
    $$;
    CREATE FUNCTION protect_held_record() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF record_is_held(TG_ARGV[0],OLD.id,current_timestamp)
      THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      RETURN OLD;
    END $$;
    """)
    for table, kind in [
        ("consent_records", "CONSENT"),
        ("attempts", "ATTEMPT"),
        ("content_flags", "CONTENT_FLAG"),
        ("data_subject_requests", "DATA_REQUEST"),
    ]:
        op.execute(f"""CREATE TRIGGER aa_protect_held_record BEFORE DELETE ON {table}
        FOR EACH ROW EXECUTE FUNCTION protect_held_record('{kind}')""")


def downgrade() -> None:
    raise RuntimeError("Preserve holds and evidence; disable routes and use a forward fix")
