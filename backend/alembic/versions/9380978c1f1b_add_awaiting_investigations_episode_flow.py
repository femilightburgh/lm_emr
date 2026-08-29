"""
add awaiting investigations episode flow

Revision ID: 9380978c1f1b
Revises: 0acd378dd63a
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9380978c1f1b"
down_revision: Union[str, Sequence[str], None] = "0acd378dd63a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE episode_flow_status_enum
        ADD VALUE IF NOT EXISTS 'AWAITING_INVESTIGATIONS'
        """
    )


def downgrade() -> None:
    # PostgreSQL does not support removing a single enum value safely
    # with ALTER TYPE. Leave the value in place on downgrade.
    pass
