"""
add episode admitted clinical event type

Revision ID: <GENERATED_REVISION>
Revises: de680f9502e8
Create Date: 2026-08-16

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c04993ca379b"
down_revision: Union[str, Sequence[str], None] = "de680f9502e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add EPISODE_ADMITTED to the PostgreSQL Clinical Event enum.
    """

    op.execute(
        """
        ALTER TYPE clinical_event_type_enum
        ADD VALUE IF NOT EXISTS 'EPISODE_ADMITTED'
        """
    )


def downgrade() -> None:
    """
    PostgreSQL does not support removing an individual value from
    an enum safely with a simple ALTER TYPE statement.

    Downgrade is intentionally left empty.
    """
    pass