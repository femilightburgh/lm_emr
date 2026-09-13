"""add awaiting pharmacy episode flow status

Revision ID: ADD_AWAITING_PHARMACY
Revises: 5d8e9f0a1b2c
"""

from alembic import op


revision = "ADD_AWAITING_PHARMACY"
down_revision = "5d8e9f0a1b2c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE episode_flow_status_enum
        ADD VALUE IF NOT EXISTS 'AWAITING_PHARMACY'
        """
    )


def downgrade() -> None:
    # PostgreSQL does not support removing an individual enum value
    # safely from an enum type without recreating the type.
    pass
