"""ADR-067: immutable operational warning configuration and audited pointer."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    schema = connection.scalar(text("SELECT current_schema()"))
    if not isinstance(schema, str):
        raise RuntimeError("Configuration migration requires an explicit schema")
    quoted = connection.dialect.identifier_preparer.quote_schema(schema)
    source = Path(__file__).resolve().parents[1] / "sql" / "0043_operations_configuration.sql"
    op.execute(source.read_text().replace("__SCHEMA__", quoted))


def downgrade() -> None:
    raise RuntimeError("Preserve configuration versions and audit; use a forward repair")
