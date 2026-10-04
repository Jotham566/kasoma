"""FR-OPS-002: indexes for bounded local queue cohorts and feedback timing."""

from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE INDEX inbound_status_received ON inbound_messages(status,received_at);
    CREATE INDEX outbound_status_created ON outbound_messages(status,created_at);
    CREATE INDEX outbound_feedback_sent ON outbound_messages(sent_at DESC,id)
      WHERE template='PRACTICE_FEEDBACK' AND sent_at IS NOT NULL;
    CREATE INDEX outbound_accepted_created ON outbound_messages(created_at)
      WHERE sent_at IS NOT NULL;
    """)


def downgrade() -> None:
    raise RuntimeError("Use a reviewed forward fix for operational index changes")
