"""Require a terminal flag's retention deadline explicitly (SQL NULL is not false)."""

from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE content_flags ADD CONSTRAINT terminal_flag_retention_required
      CHECK(status NOT IN ('RESOLVED','DISMISSED') OR retention_due_at IS NOT NULL);
    """)


def downgrade() -> None:
    raise RuntimeError("Retain the privacy guard and use a forward fix")
