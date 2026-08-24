"""
add clinical order cancelled event type

Revision ID: 7c0a4f5d1b2e
Revises: 5214042f4210
Create Date: 2026-08-24
"""

from typing import Sequence, Union

from alembic import op


revision: str = "7c0a4f5d1b2e"
down_revision: Union[str, Sequence[str], None] = "5214042f4210"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add CLINICAL_ORDER_CANCELLED to the PostgreSQL Clinical Event enum.
    """

    op.execute(
        """
        ALTER TYPE clinical_event_type_enum
        ADD VALUE IF NOT EXISTS 'CLINICAL_ORDER_CANCELLED'
        """
    )


def downgrade() -> None:
    """
    PostgreSQL does not support removing a single enum value safely.
    """

    pass
