"""add coalition_config to bidding_game_simulations

Revision ID: a4e2d8f1b3c7
Revises: f11c2a8e9b7d
Create Date: 2026-04-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4e2d8f1b3c7'
down_revision: Union[str, None] = 'f11c2a8e9b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'bidding_game_simulations',
        sa.Column('coalition_config', sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('bidding_game_simulations', 'coalition_config')
