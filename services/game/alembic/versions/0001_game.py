"""game tables

Revision ID: 0001_game
Revises:
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_game"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("user_id", sa.Uuid(), primary_key=True),
        sa.Column("capital", sa.Integer(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_players_rank", "players", ["capital", "user_id"])
    op.create_table(
        "buildings",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("players.user_id"), primary_key=True),
        sa.Column("building_id", sa.String(32), primary_key=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("passed_steps", sa.Integer(), nullable=False),
        sa.Column("total_steps", sa.Integer(), nullable=False),
        sa.Column("current_title", sa.String(200), nullable=False),
        sa.Column("next_condition", sa.String(200), nullable=False),
    )
    op.create_table(
        "ledger",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("players.user_id"), nullable=False),
        sa.Column("reason", sa.String(32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("capital_delta", sa.Integer(), nullable=False),
        sa.Column("xp_delta", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("reason", "source_id"),
    )
    op.create_table(
        "balance_config",
        sa.Column("key", sa.String(32), primary_key=True),
        sa.Column("value", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("balance_config")
    op.drop_table("ledger")
    op.drop_table("buildings")
    op.drop_index("ix_players_rank", table_name="players")
    op.drop_table("players")
