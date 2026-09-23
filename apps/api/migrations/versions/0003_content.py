"""Content review, identity roles and append-only audit (FR-CNT-001–005)."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def uid(
    name: str = "id", reference: str | None = None, primary: bool = False, nullable: bool = False
) -> sa.Column[UUID]:
    args = [sa.ForeignKey(reference)] if reference else []
    return sa.Column(name, sa.Uuid(), *args, primary_key=primary, nullable=nullable)


def stamp(name: str) -> sa.Column[datetime]:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "user_roles",
        uid("user_id", "users.id", True),
        sa.Column("role", sa.String(32), primary_key=True),
        stamp("granted_at"),
        sa.CheckConstraint(
            "role IN ('CONTENT_AUTHOR','ACADEMIC_REVIEWER','ADMIN','SUPPORT_READONLY')"
        ),
    )
    op.create_table(
        "concepts",
        uid(primary=True),
        uid("topic_id", "topics.id"),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("syllabus_reference", sa.Text(), nullable=False),
        sa.Column("synthetic", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "competencies",
        uid(primary=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
    )
    op.create_table(
        "items",
        uid(primary=True),
        uid("subject_id", "subjects.id"),
        uid("author_id", "users.id"),
        stamp("created_at"),
    )
    op.create_table(
        "item_versions",
        uid(primary=True),
        uid("item_id", "items.id"),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("review_round", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        uid("author_id", "users.id"),
        uid("topic_id", "topics.id", nullable=True),
        uid("concept_id", "concepts.id", nullable=True),
        sa.Column("document", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("requires_second_review", sa.Boolean(), nullable=False),
        sa.Column("synthetic", sa.Boolean(), nullable=False),
        stamp("created_at"),
        stamp("updated_at"),
        sa.UniqueConstraint("item_id", "version"),
        sa.CheckConstraint("version > 0 AND revision > 0 AND review_round >= 0"),
        sa.CheckConstraint("status IN ('DRAFT','IN_REVIEW','APPROVED','RETIRED')"),
    )
    op.create_table(
        "item_mappings",
        uid("item_version_id", "item_versions.id", True),
        uid("competency_id", "competencies.id", True),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.CheckConstraint("weight > 0 AND weight <= 1"),
    )
    op.create_table(
        "content_reviews",
        uid(primary=True),
        uid("item_version_id", "item_versions.id"),
        uid("reviewer_id", "users.id"),
        sa.Column("content_hash", sa.Text(), nullable=False),
        sa.Column("review_round", sa.Integer(), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("checklist", sa.JSON(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        stamp("created_at"),
        sa.UniqueConstraint("item_version_id", "review_round", "reviewer_id"),
        sa.CheckConstraint("decision IN ('APPROVE','RETURN')"),
    )
    op.create_table(
        "audit_log",
        uid(primary=True),
        uid("actor_id", "users.id", nullable=True),
        uid("target_id"),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        uid("request_id"),
        sa.Column("before_hash", sa.Text()),
        sa.Column("after_hash", sa.Text()),
        stamp("created_at"),
    )
    op.create_table(
        "content_mutation_receipts",
        uid("actor_id", "users.id", True),
        uid("key", primary=True),
        sa.Column("request_hash", sa.Text(), nullable=False),
        uid("item_version_id", "item_versions.id"),
    )
    op.create_table(
        "content_outbox_events",
        uid(primary=True),
        uid("item_version_id", "item_versions.id"),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        uid("request_id"),
        stamp("created_at"),
    )
    for table, columns in {
        "item_versions": ["item_id", "status"],
        "content_reviews": ["item_version_id"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])
    op.execute("""
        CREATE FUNCTION reject_content_history_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'Content history is append-only'; END $$
    """)
    for table in ["audit_log", "content_reviews", "items"]:
        op.execute(
            f"CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION reject_content_history_mutation()"
        )
    op.execute("""
        CREATE FUNCTION guard_item_version() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE approvals integer;
        BEGIN
          IF TG_OP = 'DELETE' THEN RAISE EXCEPTION 'Version deletion prohibited'; END IF;
          IF TG_OP = 'INSERT' THEN
            IF NEW.status <> 'DRAFT' THEN RAISE EXCEPTION 'New versions must be drafts'; END IF;
            RETURN NEW;
          END IF;
          IF NEW.id <> OLD.id OR NEW.item_id <> OLD.item_id OR NEW.author_id <> OLD.author_id
            OR NEW.version <> OLD.version OR NEW.synthetic <> OLD.synthetic
            OR NEW.created_at <> OLD.created_at OR NEW.revision <> OLD.revision + 1 THEN
            RAISE EXCEPTION 'Version identity or revision invalid';
          END IF;
          IF OLD.requires_second_review AND NOT NEW.requires_second_review THEN
            RAISE EXCEPTION 'Review escalation cannot be removed';
          END IF;
          IF OLD.status <> 'DRAFT' AND (
            NEW.document::jsonb <> OLD.document::jsonb OR NEW.content_hash <> OLD.content_hash
            OR NEW.topic_id IS DISTINCT FROM OLD.topic_id
            OR NEW.concept_id IS DISTINCT FROM OLD.concept_id) THEN
            RAISE EXCEPTION 'Published or reviewing content is immutable';
          END IF;
          IF NOT ((OLD.status = 'DRAFT' AND NEW.status IN ('DRAFT','IN_REVIEW'))
            OR (OLD.status = 'IN_REVIEW' AND NEW.status IN ('IN_REVIEW','DRAFT','APPROVED'))
            OR (OLD.status = 'APPROVED' AND NEW.status = 'RETIRED')) THEN
            RAISE EXCEPTION 'Invalid content transition';
          END IF;
          IF NEW.status = 'APPROVED' THEN
            SELECT count(DISTINCT reviewer_id) INTO approvals FROM content_reviews
              WHERE item_version_id = NEW.id AND review_round = NEW.review_round
              AND decision = 'APPROVE' AND reviewer_id <> NEW.author_id
              AND content_hash = NEW.content_hash;
            IF approvals < (CASE WHEN NEW.requires_second_review THEN 2 ELSE 1 END) THEN
              RAISE EXCEPTION 'Independent approval required';
            END IF;
          END IF;
          RETURN NEW;
        END $$
    """)
    op.execute(
        "CREATE TRIGGER protect_version BEFORE INSERT OR UPDATE OR DELETE ON item_versions "
        "FOR EACH ROW EXECUTE FUNCTION guard_item_version()"
    )
    op.execute("""
        CREATE FUNCTION guard_item_mapping() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE parent uuid; state text;
        BEGIN
          IF TG_OP = 'DELETE' THEN parent := OLD.item_version_id;
          ELSE parent := NEW.item_version_id; END IF;
          IF TG_OP = 'UPDATE' AND NEW.item_version_id <> OLD.item_version_id THEN
            RAISE EXCEPTION 'Mapping parent is immutable';
          END IF;
          SELECT status INTO state FROM item_versions WHERE id = parent FOR UPDATE;
          IF state <> 'DRAFT' THEN RAISE EXCEPTION 'Frozen mapping'; END IF;
          IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
        END $$
    """)
    op.execute(
        "CREATE TRIGGER protect_mapping BEFORE INSERT OR UPDATE OR DELETE ON item_mappings "
        "FOR EACH ROW EXECUTE FUNCTION guard_item_mapping()"
    )
    op.execute("""
        CREATE FUNCTION guard_content_review() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE author uuid; state text;
        BEGIN
          SELECT author_id, status INTO author, state FROM item_versions
            WHERE id = NEW.item_version_id FOR UPDATE;
          IF NEW.reviewer_id = author OR state <> 'IN_REVIEW' THEN
            RAISE EXCEPTION 'Independent review of submitted content required';
          END IF;
          RETURN NEW;
        END $$
    """)
    op.execute(
        "CREATE TRIGGER protect_review BEFORE INSERT ON content_reviews "
        "FOR EACH ROW EXECUTE FUNCTION guard_content_review()"
    )


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade requires explicit approval and a recovery plan")
