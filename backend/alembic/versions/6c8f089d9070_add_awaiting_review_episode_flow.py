"""add awaiting review episode flow

Revision ID: 6c8f089d9070
Revises: 5805c6b49261
Create Date: 2026-08-26 19:58:03.778300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c8f089d9070'
down_revision: Union[str, Sequence[str], None] = '5805c6b49261'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AWAITING_REVIEW to the Episode flow status enum."""
    op.execute(
        """
        ALTER TYPE episode_flow_status_enum
        ADD VALUE IF NOT EXISTS 'AWAITING_REVIEW'
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
