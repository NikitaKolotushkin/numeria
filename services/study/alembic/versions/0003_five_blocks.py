"""five blocks in every building

Revision ID: 0003_five_blocks
Revises: 0002_question_active
"""

from alembic import op
from sqlalchemy import bindparam, text

from app.catalog import planned_blocks

revision = "0003_five_blocks"
down_revision = "0002_question_active"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    keep = {str(block_id) for _discipline, _order, _title, block_id in planned_blocks()}
    existing = [row[0] for row in bind.execute(text("SELECT id FROM blocks"))]
    drop = [item for item in existing if str(item) not in keep]
    if drop:
        _delete_blocks(bind, drop)
    present = {str(item) for item in existing}
    for discipline_id, sort_order, title, block_id in planned_blocks():
        if str(block_id) in present:
            continue
        bind.execute(
            text(
                "INSERT INTO blocks (id, discipline_id, title, sort_order) "
                "VALUES (:id, :discipline_id, :title, :sort_order)"
            ),
            {
                "id": block_id if bind.dialect.name == "postgresql" else str(block_id),
                "discipline_id": discipline_id,
                "title": title,
                "sort_order": sort_order,
            },
        )


def _delete_blocks(bind, drop: list) -> None:
    ids = drop if bind.dialect.name == "postgresql" else [str(item) for item in drop]
    params = {"ids": ids}
    statements = [
        """
        DELETE FROM quiz_attempt_answers
        WHERE attempt_id IN (SELECT id FROM quiz_attempts WHERE block_id IN :ids)
           OR question_id IN (SELECT id FROM questions WHERE block_id IN :ids)
        """,
        "DELETE FROM block_progress WHERE block_id IN :ids",
        "DELETE FROM quiz_attempts WHERE block_id IN :ids",
        "DELETE FROM options WHERE question_id IN (SELECT id FROM questions WHERE block_id IN :ids)",
        "DELETE FROM questions WHERE block_id IN :ids",
        "DELETE FROM block_snapshots WHERE block_id IN :ids",
        "DELETE FROM blocks WHERE id IN :ids",
    ]
    for statement in statements:
        bind.execute(text(statement).bindparams(bindparam("ids", expanding=True)), params)


def downgrade() -> None:
    raise NotImplementedError
