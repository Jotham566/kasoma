"""Preserve a calibration band's subject/topic binding after curriculum updates."""

from alembic import op

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE topics ADD CONSTRAINT topics_id_subject_key UNIQUE(id,subject_id);
    ALTER TABLE grading_bands ADD CONSTRAINT grading_band_topic_subject_fk
      FOREIGN KEY(topic_id,subject_id) REFERENCES topics(id,subject_id);
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve calibration scope binding and use a forward fix")
