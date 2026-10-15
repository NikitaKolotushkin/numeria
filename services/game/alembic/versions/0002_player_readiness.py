"""player readiness from the registration quiz

Revision ID: 0002_player_readiness
Revises: 0001_game
Create Date: 2026-10-15
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_player_readiness"
down_revision = "0001_game"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "players",
        sa.Column("readiness", sa.String(80), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("players", "readiness")
