"""users tables

Revision ID: 0001_users
Revises:
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(80), nullable=False),
        sa.Column("last_name", sa.String(80), nullable=False),
        sa.Column("university", sa.String(160), nullable=False),
        sa.Column("direction", sa.String(160), nullable=False),
        sa.Column("course", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "consents",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("personal_data_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("terms_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ai_assessment_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_version", sa.String(32), nullable=False),
    )
    op.create_table(
        "hobbies",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("hobby_id", sa.String(32), primary_key=True),
    )
    op.create_table(
        "onboarding_answers",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("question_id", sa.Integer(), primary_key=True),
        sa.Column("option_index", sa.Integer(), nullable=False),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "access_denylist",
        sa.Column("jti", sa.Uuid(), primary_key=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("access_denylist")
    op.drop_table("refresh_tokens")
    op.drop_table("onboarding_answers")
    op.drop_table("hobbies")
    op.drop_table("consents")
    op.drop_table("users")
