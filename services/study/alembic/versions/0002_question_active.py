"""keep retired quiz questions after a retry

Revision ID: 0002_question_active
Revises: 0001_study
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_question_active"
down_revision = "0001_study"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            DECLARE cname text;
            BEGIN
              SELECT conname INTO cname
              FROM pg_constraint
              WHERE conrelid = 'questions'::regclass AND contype = 'u';
              IF cname IS NOT NULL THEN
                EXECUTE format('ALTER TABLE questions DROP CONSTRAINT %I', cname);
              END IF;
            END $$;
            """
        )
        op.create_index(
            "uq_questions_active_slot",
            "questions",
            ["user_id", "block_id", "sort_order"],
            unique=True,
            postgresql_where=sa.text("active"),
        )
    else:
        op.drop_constraint("uq_questions_user_id_block_id_sort_order", "questions", type_="unique")
        op.execute(
            "CREATE UNIQUE INDEX uq_questions_active_slot ON questions (user_id, block_id, sort_order) WHERE active = 1"
        )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_questions_active_slot")
    op.create_unique_constraint("uq_questions_user_id_block_id_sort_order", "questions", ["user_id", "block_id", "sort_order"])
    op.drop_column("questions", "active")
