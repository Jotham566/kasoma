"""ADR-060: default-disabled, isolated synthetic export evidence retirement."""

from alembic import op

from services.export_retirement_install import install_v1

revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    install_v1(op.get_bind())


def downgrade() -> None:
    raise RuntimeError("Disable retirement; preserve exact holds and use a forward fix")
