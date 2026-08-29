"""add received clinical order status

Revision ID: 0f2046a9aa21
Revises: 1b6fc56a0c88
Create Date: 2026-08-27 07:18:42.220146
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0f2046a9aa21"
down_revision: Union[str, Sequence[str], None] = "1b6fc56a0c88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE clinical_order_status_enum
        ADD VALUE IF NOT EXISTS 'RECEIVED'
        AFTER 'REQUESTED'
        """
    )


def downgrade() -> None:
    # PostgreSQL does not support removing an enum value directly.
    # Downgrade is intentionally a no-op until the enum is rebuilt safely.
    pass
