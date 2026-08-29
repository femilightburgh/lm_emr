"""create prescriptions

Revision ID: 8ae5109bfce8
Revises: bb5c652bb168
Create Date: 2026-08-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8ae5109bfce8"
down_revision: Union[str, Sequence[str], None] = "bb5c652bb168"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prescriptions",
        sa.Column(
            "clinical_order_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "medicine_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "strength",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "dose",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "dose_unit",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "route",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "frequency",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "duration",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "duration_unit",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "quantity",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "directions",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "indication",
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
            ["clinical_order_id"],
            ["clinical_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinical_order_id",
            name="uq_prescriptions_clinical_order_id",
        ),
    )

    op.create_index(
        "ix_prescriptions_clinical_order_id",
        "prescriptions",
        ["clinical_order_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prescriptions_clinical_order_id",
        table_name="prescriptions",
    )

    op.drop_table("prescriptions")
