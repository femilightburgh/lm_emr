"""add nursing intake clinical document type

Revision ID: 106da7d2bcac
Revises: 57dc4a524bbf
Create Date: 2026-08-23 09:49:02.944909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "106da7d2bcac"
down_revision: Union[str, Sequence[str], None] = "57dc4a524bbf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add NURSING_INTAKE to the clinical document type enum."""

    op.execute(
        """
        ALTER TYPE clinical_document_type_enum
        ADD VALUE IF NOT EXISTS 'NURSING_INTAKE'
        """
    )


def downgrade() -> None:
    """
    PostgreSQL does not support removing an enum value directly.

    The value is intentionally left in place during downgrade.
    """

    pass