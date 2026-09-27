"""add custom investigation name

Revision ID: 7b2e9d683245
Revises: ADD_AWAITING_PHARMACY
Create Date: 2026-09-23 23:54:13.297326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b2e9d683245'
down_revision: Union[str, Sequence[str], None] = 'ADD_AWAITING_PHARMACY'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "clinical_order_items",
        sa.Column("custom_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("clinical_order_items", "custom_name")
