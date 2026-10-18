"""Atomic publication ordinal and minimum-ten-percent audit assignment ledger."""

from alembic import op

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE grading_publication_counters (
      band_id uuid PRIMARY KEY REFERENCES grading_bands,
      returned_grades bigint NOT NULL DEFAULT 0 CHECK(returned_grades BETWEEN 0 AND 1000000000),
      assigned_audits bigint NOT NULL DEFAULT 0,
      CHECK(assigned_audits=(returned_grades+9)/10));
    CREATE TABLE grading_publications (
      attempt_id uuid PRIMARY KEY REFERENCES grades(attempt_id),
      band_id uuid NOT NULL REFERENCES grading_bands,
      ordinal bigint NOT NULL CHECK(ordinal BETWEEN 1 AND 1000000000),
      audit_required boolean NOT NULL,
      published_at timestamptz NOT NULL,
      UNIQUE(band_id,ordinal),
      CHECK(audit_required=((ordinal-1)%10=0)));
    CREATE TABLE grading_audit_assignments (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      attempt_id uuid NOT NULL UNIQUE REFERENCES grading_publications(attempt_id),
      assigned_at timestamptz NOT NULL);

    CREATE FUNCTION grading_publication_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE band grading_bands%ROWTYPE; next_ordinal bigint;
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Grading publication is immutable'; END IF;
      SELECT * INTO band FROM grading_bands WHERE id=NEW.band_id FOR UPDATE;
      IF NOT FOUND OR NOT band.enabled OR band.activated_at>NEW.published_at THEN
        RAISE EXCEPTION 'Enabled current band required'; END IF;
      IF NOT EXISTS(SELECT 1 FROM grades g JOIN attempts a ON a.id=g.attempt_id
        JOIN item_versions v ON v.id=a.item_version_id JOIN items i ON i.id=v.item_id
        WHERE a.id=NEW.attempt_id AND a.item_version_id=g.item_version_id
          AND i.subject_id=band.subject_id AND v.topic_id=band.topic_id
          AND a.submitted_at<=NEW.published_at)
      THEN RAISE EXCEPTION 'Publication scope must match the definitive grade'; END IF;
      SELECT returned_grades+1 INTO next_ordinal FROM grading_publication_counters
        WHERE band_id=NEW.band_id FOR UPDATE;
      IF NOT FOUND THEN RAISE EXCEPTION 'Publication counter unavailable'; END IF;
      NEW.ordinal:=next_ordinal;
      NEW.audit_required:=((next_ordinal-1)%10=0);
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_grading_publication BEFORE INSERT OR UPDATE OR DELETE
      ON grading_publications FOR EACH ROW EXECUTE FUNCTION grading_publication_guard();

    CREATE FUNCTION grading_audit_assignment_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Grading audit assignment is immutable'; END IF;
      IF NOT EXISTS(SELECT 1 FROM grading_publications p
        WHERE p.attempt_id=NEW.attempt_id AND p.audit_required AND p.published_at=NEW.assigned_at)
      THEN RAISE EXCEPTION 'Audit assignment must match a sampled publication'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER bound_grading_audit_assignment BEFORE INSERT OR UPDATE OR DELETE
      ON grading_audit_assignments FOR EACH ROW EXECUTE FUNCTION grading_audit_assignment_guard();

    CREATE FUNCTION grading_publication_counter_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE sampled boolean;
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Publication ordinals cannot be reset'; END IF;
      IF TG_OP='INSERT' THEN
        IF NEW.returned_grades<>0 OR NEW.assigned_audits<>0
          OR EXISTS(SELECT 1 FROM grading_publications WHERE band_id=NEW.band_id)
        THEN RAISE EXCEPTION 'Publication counter must start empty'; END IF;
      ELSE
        IF NEW.band_id<>OLD.band_id OR NEW.returned_grades<>OLD.returned_grades+1
        THEN RAISE EXCEPTION 'Publication counter must advance once'; END IF;
        SELECT audit_required INTO sampled FROM grading_publications
          WHERE band_id=NEW.band_id AND ordinal=NEW.returned_grades;
        IF NOT FOUND OR NEW.assigned_audits<>OLD.assigned_audits+sampled::integer
          OR (sampled AND NOT EXISTS(SELECT 1 FROM grading_audit_assignments a
            JOIN grading_publications p ON p.attempt_id=a.attempt_id
            WHERE p.band_id=NEW.band_id AND p.ordinal=NEW.returned_grades))
        THEN RAISE EXCEPTION 'Publication and audit must precede counter advancement'; END IF;
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER protect_grading_publication_counter BEFORE INSERT OR UPDATE OR DELETE
      ON grading_publication_counters FOR EACH ROW
      EXECUTE FUNCTION grading_publication_counter_guard();
    INSERT INTO grading_publication_counters(band_id) SELECT id FROM grading_bands;
    CREATE FUNCTION initialize_grading_publication_counter() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      INSERT INTO grading_publication_counters(band_id) VALUES(NEW.id);
      RETURN NEW;
    END $$;
    CREATE TRIGGER initialize_grading_publication_counter AFTER INSERT ON grading_bands
      FOR EACH ROW EXECUTE FUNCTION initialize_grading_publication_counter();

    CREATE FUNCTION record_grading_publication() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.audit_required THEN
        INSERT INTO grading_audit_assignments(attempt_id,assigned_at)
          VALUES(NEW.attempt_id,NEW.published_at);
      END IF;
      UPDATE grading_publication_counters SET returned_grades=NEW.ordinal,
        assigned_audits=assigned_audits+NEW.audit_required::integer WHERE band_id=NEW.band_id;
      RETURN NEW;
    END $$;
    CREATE TRIGGER record_grading_publication AFTER INSERT ON grading_publications
      FOR EACH ROW EXECUTE FUNCTION record_grading_publication();
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve publication/audit evidence and apply a forward fix")
