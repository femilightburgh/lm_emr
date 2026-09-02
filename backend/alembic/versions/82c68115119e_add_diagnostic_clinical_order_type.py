"""
add diagnostic clinical order type

Revision ID: 82c68115119e
Revises: 803b629883aa
"""

from typing import Sequence, Union

from alembic import op


revision: str = "82c68115119e"
down_revision: Union[str, Sequence[str], None] = "803b629883aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE clinical_order_type_enum
        ADD VALUE IF NOT EXISTS 'DIAGNOSTIC'
        """
    )


def downgrade() -> None:
    """
    PostgreSQL does not support removing an individual enum value.

    The DIAGNOSTIC value is therefore intentionally retained on downgrade.
    """
    pass
