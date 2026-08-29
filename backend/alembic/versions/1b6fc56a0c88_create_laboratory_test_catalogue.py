"""
create laboratory test catalogue

Revision ID: 1b6fc56a0c88
Revises: 6c8f089d9070
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "1b6fc56a0c88"
down_revision: Union[str, Sequence[str], None] = "6c8f089d9070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "laboratory_tests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "specimen",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "result_fields",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "code",
            name="uq_laboratory_test_code",
        ),
    )

    op.create_index(
        "ix_laboratory_tests_code",
        "laboratory_tests",
        ["code"],
    )

    op.create_index(
        "ix_laboratory_tests_name",
        "laboratory_tests",
        ["name"],
    )

    op.create_index(
        "ix_laboratory_tests_active",
        "laboratory_tests",
        ["active"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_laboratory_tests_active",
        table_name="laboratory_tests",
    )

    op.drop_index(
        "ix_laboratory_tests_name",
        table_name="laboratory_tests",
    )

    op.drop_index(
        "ix_laboratory_tests_code",
        table_name="laboratory_tests",
    )

    op.drop_table("laboratory_tests")
