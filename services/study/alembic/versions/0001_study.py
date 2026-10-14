"""study tables

Revision ID: 0001_study
Revises:
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_study"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "modules",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("building_id", sa.String(32), nullable=False, unique=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, unique=True),
    )
    op.create_table(
        "disciplines",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("module_id", sa.String(64), sa.ForeignKey("modules.id"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("module_id", "sort_order"),
    )
    op.create_table(
        "blocks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("discipline_id", sa.String(64), sa.ForeignKey("disciplines.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("discipline_id", "sort_order"),
    )
    op.create_table(
        "block_snapshots",
        sa.Column("user_id", sa.Uuid(), primary_key=True),
        sa.Column("block_id", sa.Uuid(), sa.ForeignKey("blocks.id"), primary_key=True),
        sa.Column("theory_markdown", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("block_id", sa.Uuid(), sa.ForeignKey("blocks.id"), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("user_id", "block_id", "sort_order"),
    )
    op.create_table(
        "options",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("question_id", sa.Uuid(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("question_id", "sort_order"),
    )
    op.create_table(
        "bosses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("module_id", sa.String(64), sa.ForeignKey("modules.id"), nullable=False, unique=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("pass_score", sa.Integer(), nullable=False),
    )
    op.create_table(
        "boss_snapshots",
        sa.Column("user_id", sa.Uuid(), primary_key=True),
        sa.Column("boss_id", sa.Uuid(), sa.ForeignKey("bosses.id"), primary_key=True),
        sa.Column("prompt_markdown", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("block_id", sa.Uuid(), sa.ForeignKey("blocks.id"), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_quiz_attempts_user_block", "quiz_attempts", ["user_id", "block_id", "created_at"])
    op.create_table(
        "quiz_attempt_answers",
        sa.Column("attempt_id", sa.Uuid(), sa.ForeignKey("quiz_attempts.id"), primary_key=True),
        sa.Column("question_id", sa.Uuid(), sa.ForeignKey("questions.id"), primary_key=True),
        sa.Column("option_id", sa.Uuid(), sa.ForeignKey("options.id"), nullable=False),
    )
    op.create_table(
        "boss_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("boss_id", sa.Uuid(), sa.ForeignKey("bosses.id"), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer()),
        sa.Column("verdict", sa.String(16)),
        sa.Column("review_text", sa.Text()),
        sa.Column("growth_zones", sa.JSON(), nullable=False),
        sa.Column("passed", sa.Boolean()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_boss_attempts_user_boss", "boss_attempts", ["user_id", "boss_id", "created_at"])
    op.create_table(
        "block_progress",
        sa.Column("user_id", sa.Uuid(), primary_key=True),
        sa.Column("block_id", sa.Uuid(), sa.ForeignKey("blocks.id"), primary_key=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("passed_attempt_id", sa.Uuid(), sa.ForeignKey("quiz_attempts.id")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "boss_progress",
        sa.Column("user_id", sa.Uuid(), primary_key=True),
        sa.Column("boss_id", sa.Uuid(), sa.ForeignKey("bosses.id"), primary_key=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("passed_attempt_id", sa.Uuid(), sa.ForeignKey("boss_attempts.id")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "applied_commands",
        sa.Column("reason", sa.String(32), primary_key=True),
        sa.Column("source_id", sa.Uuid(), primary_key=True),
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE UNIQUE INDEX uq_options_one_correct ON options (question_id) WHERE is_correct")
    else:
        op.execute("CREATE UNIQUE INDEX uq_options_one_correct ON options (question_id) WHERE is_correct = 1")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_options_one_correct")
    op.drop_table("applied_commands")
    op.drop_table("boss_progress")
    op.drop_table("block_progress")
    op.drop_index("ix_boss_attempts_user_boss", table_name="boss_attempts")
    op.drop_table("boss_attempts")
    op.drop_table("quiz_attempt_answers")
    op.drop_index("ix_quiz_attempts_user_block", table_name="quiz_attempts")
    op.drop_table("quiz_attempts")
    op.drop_table("boss_snapshots")
    op.drop_table("bosses")
    op.drop_table("options")
    op.drop_table("questions")
    op.drop_table("block_snapshots")
    op.drop_table("blocks")
    op.drop_table("disciplines")
    op.drop_table("modules")
