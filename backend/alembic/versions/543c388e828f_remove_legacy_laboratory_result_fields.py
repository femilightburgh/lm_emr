"""
remove legacy laboratory result fields

Revision ID: 543c388e828f
Revises: 21521b547900
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "543c388e828f"
down_revision: Union[str, Sequence[str], None] = "21521b547900"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        "laboratory_tests",
        "result_fields",
    )


def downgrade() -> None:
    op.add_column(
        "laboratory_tests",
        sa.Column(
            "result_fields",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )

    op.alter_column(
        "laboratory_tests",
        "result_fields",
        server_default=None,
    )
