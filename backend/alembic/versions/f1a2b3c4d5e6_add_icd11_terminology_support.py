"""add icd11 terminology support

Revision ID: f1a2b3c4d5e6
Revises: ae12b3c4d5e6
Create Date: 2026-09-06
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import Column, String


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "ae12b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE terminology_system_enum "
        "ADD VALUE IF NOT EXISTS 'ICD_11'"
    )
    op.add_column(
        "terminology_concepts",
        Column("uri", String(length=2048), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("terminology_concepts", "uri")
    # PostgreSQL does not support removing an enum value safely.
    # The ICD_11 enum value is intentionally retained on downgrade.
