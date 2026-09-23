"""Add vector availability and the frozen curriculum catalog.

Revision ID: 0001
Revises: none
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "levels",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
    )
    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("level_id", sa.Uuid(), sa.ForeignKey("levels.id"), nullable=False),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
    )
    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("subject_id", sa.Uuid(), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False, unique=True),
    )


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade requires explicit approval and a recovery plan")
