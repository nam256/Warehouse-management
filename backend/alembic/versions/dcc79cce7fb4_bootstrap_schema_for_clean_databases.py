"""bootstrap schema for clean databases

Revision ID: dcc79cce7fb4
Revises: 40c2b4a9e4fc
Create Date: 2026-07-18 14:53:37.273567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app import models  # noqa: F401
from app.database import Base


# revision identifiers, used by Alembic.
revision: str = 'dcc79cce7fb4'
down_revision: Union[str, Sequence[str], None] = '40c2b4a9e4fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if sa.inspect(bind).has_table("stock_batches"):
        return

    # This bridge revision supports a new database while the preceding revision
    # upgrades databases created by the application's former create_all path.
    for table in Base.metadata.sorted_tables:
        table.create(bind=bind, checkfirst=True)

    with op.batch_alter_table("production_orders") as batch_op:
        batch_op.create_foreign_key(
            "fk_production_orders_output_batch_id",
            "stock_batches",
            ["output_batch_id"],
            ["id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
