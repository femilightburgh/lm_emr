"""create clinical results

Revision ID: 5805c6b49261
Revises: bd801cdac8fa
Create Date: 2026-08-26 19:44:00.897463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5805c6b49261'
down_revision: Union[str, Sequence[str], None] = 'bd801cdac8fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
