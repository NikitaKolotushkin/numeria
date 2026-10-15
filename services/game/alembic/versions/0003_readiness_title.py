"""shorten the top readiness title

Revision ID: 0003_readiness_title
Revises: 0002_player_readiness
Create Date: 2026-10-15
"""

from alembic import op

revision = "0003_readiness_title"
down_revision = "0002_player_readiness"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE players SET readiness = 'Подготовленный' "
        "WHERE readiness = 'Подготовленный пользователь'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE players SET readiness = 'Подготовленный пользователь' "
        "WHERE readiness = 'Подготовленный'"
    )
