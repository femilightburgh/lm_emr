"""create medication dispensing

Revision ID: d49d5295ce72
Revises: 8ae5109bfce8
Create Date: 2026-08-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d49d5295ce72"
down_revision: Union[str, Sequence[str], None] = "8ae5109bfce8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL enum values cannot be introduced through the normal
    # create/alter-table flow used by Alembic here, so add the value
    # explicitly before creating records that can use it.
    op.execute(
        """
        ALTER TYPE clinical_event_type_enum
        ADD VALUE IF NOT EXISTS 'MEDICATION_DISPENSED'
        """
    )

    op.create_table(
        "dispensings",
        sa.Column(
            "prescription_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "dispensed_by",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "quantity_dispensed",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "dispensed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.UUID(),
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
        sa.ForeignKeyConstraint(
            ["prescription_id"],
            ["prescriptions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["dispensed_by"],
            ["staff.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "prescription_id",
            name="uq_dispensings_prescription_id",
        ),
    )

    op.create_index(
        "ix_dispensings_prescription_id",
        "dispensings",
        ["prescription_id"],
        unique=True,
    )

    op.create_index(
        "ix_dispensings_dispensed_by",
        "dispensings",
        ["dispensed_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dispensings_dispensed_by",
        table_name="dispensings",
    )

    op.drop_index(
        "ix_dispensings_prescription_id",
        table_name="dispensings",
    )

    op.drop_table("dispensings")

    # PostgreSQL does not support safely removing an individual enum value
    # in place. The enum value therefore remains on downgrade.
