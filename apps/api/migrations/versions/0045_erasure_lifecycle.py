"""ADR-061: dormant synthetic erasure lifecycle; no execution capability."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0045"
down_revision = "0044"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    schema = connection.scalar(text("SELECT current_schema()"))
    if not isinstance(schema, str):
        raise RuntimeError("Erasure lifecycle requires an explicit schema")
    quoted = connection.dialect.identifier_preparer.quote_schema(schema)
    source = Path(__file__).resolve().parents[1] / "sql" / "0045_erasure_lifecycle.sql"
    op.execute(source.read_text().replace("__SCHEMA__", quoted))


def downgrade() -> None:
    raise RuntimeError("Preserve closure and rights accountability; use a forward repair")
