"""Add identity, consent and safe identity-event persistence (FR-ID-001–005)."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def uid(name: str = "id", primary: bool = False) -> sa.Column[UUID]:
    return sa.Column(name, sa.Uuid(), primary_key=primary, nullable=False)


def stamp(name: str, nullable: bool = False) -> sa.Column[datetime]:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=nullable)


def user_ref(primary: bool = False) -> sa.Column[UUID]:
    return sa.Column(
        "user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=primary, nullable=False
    )


def upgrade() -> None:
    op.create_table(
        "users",
        uid(primary=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("display_name", sa.Text()),
        sa.Column("birth_date", sa.Date()),
        stamp("created_at"),
        sa.CheckConstraint("status IN ('ACTIVE','DISABLED')"),
    )
    op.create_table(
        "user_identifiers",
        uid(primary=True),
        user_ref(),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("normalized_value_encrypted", sa.Text(), nullable=False),
        sa.Column("lookup_hash", sa.String(64), nullable=False),
        stamp("verified_at"),
        sa.UniqueConstraint("type", "lookup_hash"),
        sa.CheckConstraint("type IN ('EMAIL','PHONE')"),
    )
    op.create_table(
        "auth_sessions",
        uid(primary=True),
        user_ref(),
        uid("family"),
        sa.Column("access_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("refresh_hash", sa.String(64), nullable=False, unique=True),
        stamp("authenticated_at"),
        stamp("access_expires_at"),
        stamp("expires_at"),
        stamp("rotated_at", True),
        stamp("revoked_at", True),
    )
    op.create_table(
        "otp_challenges",
        uid(primary=True),
        sa.Column("purpose", sa.String(12), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("lookup_hash", sa.String(64), nullable=False),
        sa.Column("encrypted_identifier", sa.Text(), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        stamp("expires_at"),
        stamp("consumed_at", True),
        sa.CheckConstraint("attempts BETWEEN 0 AND 5"),
        sa.CheckConstraint("purpose IN ('LOGIN','LINK','GUARDIAN')"),
    )
    op.create_table(
        "identity_rate_buckets",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
        stamp("expires_at"),
    )
    op.create_table(
        "learner_profiles",
        user_ref(True),
        sa.Column("level_id", sa.Uuid(), sa.ForeignKey("levels.id"), nullable=False),
    )
    op.create_table(
        "learner_subjects",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("learner_profiles.user_id"), primary_key=True
        ),
        sa.Column("subject_id", sa.Uuid(), sa.ForeignKey("subjects.id"), primary_key=True),
    )
    op.create_table(
        "consent_records",
        uid(primary=True),
        user_ref(),
        sa.Column("consent_type", sa.Text(), nullable=False),
        sa.Column("basis", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("evidence_encrypted", sa.Text()),
        stamp("granted_at"),
        stamp("revoked_at", True),
        uid("idempotency_key"),
        sa.Column("request_hash", sa.Text(), nullable=False),
        sa.UniqueConstraint("user_id", "idempotency_key"),
        sa.CheckConstraint("consent_type IN ('SELF','ASSENT','GUARDIAN','WITHDRAW')"),
    )
    op.create_table(
        "identity_outbox_events",
        uid(primary=True),
        user_ref(),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        stamp("created_at"),
    )
    for table, columns in {
        "user_identifiers": ["user_id"],
        "auth_sessions": ["user_id", "family"],
        "otp_challenges": ["lookup_hash", "expires_at"],
        "identity_rate_buckets": ["expires_at"],
        "consent_records": ["user_id"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade requires explicit approval and a recovery plan")
