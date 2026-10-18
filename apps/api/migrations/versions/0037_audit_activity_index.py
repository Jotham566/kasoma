"""Bound the newest audit-window sample without modifying audit evidence."""

from alembic import op

revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_audit_activity_window", "audit_log", ["created_at", "id"])


def downgrade() -> None:
    op.drop_index("ix_audit_activity_window", table_name="audit_log")
