"""add user avatar_url and material image_url

Revision ID: a1b2c3d4e5f6
Revises: dcc79cce7fb4
Create Date: 2026-08-16 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "dcc79cce7fb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns(table)}
    return column in cols


def upgrade() -> None:
    if not _has_column("users", "avatar_url"):
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(sa.Column("avatar_url", sa.String(length=500), nullable=True))
    if not _has_column("materials", "image_url"):
        with op.batch_alter_table("materials") as batch_op:
            batch_op.add_column(sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    if _has_column("materials", "image_url"):
        with op.batch_alter_table("materials") as batch_op:
            batch_op.drop_column("image_url")
    if _has_column("users", "avatar_url"):
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_column("avatar_url")
