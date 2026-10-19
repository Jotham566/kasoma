"""ADR-060: bounded due-export operational sampling."""

from alembic import op

revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE INDEX ix_export_accountability_due
        ON data_subject_requests(retention_due_at,id)
        WHERE kind='EXPORT' AND completed_at IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_index("ix_export_accountability_due", table_name="data_subject_requests")
