"""add admitted episode status

Revision ID: de680f9502e8
Revises: 85da5ea9d7df
Create Date: 2026-08-16 07:44:22.140252

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "de680f9502e8"
down_revision: Union[str, Sequence[str], None] = "85da5ea9d7df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add ADMITTED to the PostgreSQL episode status enum.
    """

    op.execute(
        """
        ALTER TYPE episode_status_enum
        ADD VALUE IF NOT EXISTS 'ADMITTED'
        """
    )


def downgrade() -> None:
    """
    PostgreSQL does not support removing an individual enum value
    directly.

    The ADMITTED value is therefore retained on downgrade.
    """

    pass