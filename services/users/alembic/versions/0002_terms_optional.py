"""terms consent is optional

Revision ID: 0002_terms_optional
Revises: 0001_users
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_terms_optional"
down_revision = "0001_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("consents", "terms_at", existing_type=sa.DateTime(timezone=True), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE consents SET terms_at = personal_data_at WHERE terms_at IS NULL")
    op.alter_column("consents", "terms_at", existing_type=sa.DateTime(timezone=True), nullable=False)
