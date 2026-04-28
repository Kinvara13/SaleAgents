"""add_iterative_result_to_bidding_game

Revision ID: f11c2a8e9b7d
Revises: ded1f9e5651c
Create Date: 2026-04-26 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f11c2a8e9b7d"
down_revision: Union[str, Sequence[str], None] = "ded1f9e5651c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("bidding_game_simulations"):
        columns = {column["name"] for column in inspector.get_columns("bidding_game_simulations")}
        if "iterative_result" not in columns:
            op.add_column(
                "bidding_game_simulations",
                sa.Column("iterative_result", sa.JSON(), nullable=True),
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("bidding_game_simulations"):
        columns = {column["name"] for column in inspector.get_columns("bidding_game_simulations")}
        if "iterative_result" in columns:
            op.drop_column("bidding_game_simulations", "iterative_result")
