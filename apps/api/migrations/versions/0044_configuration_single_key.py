"""ADR-067: current single-key warning-version guard."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    schema = connection.scalar(text("SELECT current_schema()"))
    if not isinstance(schema, str):
        raise RuntimeError("Configuration migration requires an explicit schema")
    quoted = connection.dialect.identifier_preparer.quote_schema(schema)
    source = Path(__file__).resolve().parents[1] / "sql" / "0044_configuration_single_key.sql"
    op.execute(source.read_text().replace("__SCHEMA__", quoted))


def downgrade() -> None:
    raise RuntimeError("Preserve configuration versions and audit; use a forward repair")
