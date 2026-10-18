"""Evaluate existing finite holds when DELETE runs, preserving historical predicates."""

from alembic import op

revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION protect_held_record() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF record_is_held(TG_ARGV[0],OLD.id,clock_timestamp())
      THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      RETURN OLD;
    END $$;
    CREATE OR REPLACE FUNCTION protect_held_grade() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF record_is_held('GRADE',OLD.attempt_id,clock_timestamp())
      THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      RETURN OLD;
    END $$;
    CREATE OR REPLACE FUNCTION protect_held_request_review() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF record_is_held('DATA_REQUEST_REVIEW',OLD.request_id,clock_timestamp())
      THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      RETURN OLD;
    END $$;
    CREATE OR REPLACE FUNCTION protect_held_grading_publication()
      RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF record_is_held('GRADING_PUBLICATION',OLD.attempt_id,clock_timestamp())
      THEN RAISE EXCEPTION 'Record is legally held'; END IF;
      RETURN OLD;
    END $$;
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve current hold protection and apply a forward fix")
