"""add clinical order items

Revision ID: 47c67dab84c1
Revises: 7b3c4d5e6f70
Create Date: 2026-09-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "47c67dab84c1"
down_revision: Union[str, Sequence[str], None] = "7b3c4d5e6f70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


clinical_order_item_type_enum = sa.Enum(
    "LABORATORY",
    "DIAGNOSTIC",
    name="clinical_order_item_type_enum",
)

clinical_order_item_status_enum = sa.Enum(
    "REQUESTED",
    "RECEIVED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
    name="clinical_order_item_status_enum",
)


def upgrade() -> None:
    op.create_table(
        "clinical_order_items",
        sa.Column(
            "clinical_order_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "item_type",
            clinical_order_item_type_enum,
            nullable=False,
        ),
        sa.Column(
            "status",
            clinical_order_item_status_enum,
            nullable=False,
        ),
        sa.Column(
            "laboratory_test_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "diagnostic_investigation_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "details",
            sa.JSON(),
            nullable=False,
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
        sa.ForeignKeyConstraint(
            ["laboratory_test_id"],
            ["laboratory_tests.id"],
        ),
        sa.ForeignKeyConstraint(
            ["diagnostic_investigation_id"],
            ["diagnostic_investigations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinical_order_id",
            "laboratory_test_id",
            name="uq_clinical_order_item_laboratory_test",
        ),
        sa.UniqueConstraint(
            "clinical_order_id",
            "diagnostic_investigation_id",
            name="uq_clinical_order_item_diagnostic_investigation",
        ),
    )

    op.create_index(
        "ix_clinical_order_items_clinical_order_id",
        "clinical_order_items",
        ["clinical_order_id"],
    )
    op.create_index(
        "ix_clinical_order_items_diagnostic_investigation_id",
        "clinical_order_items",
        ["diagnostic_investigation_id"],
    )
    op.create_index(
        "ix_clinical_order_items_item_type",
        "clinical_order_items",
        ["item_type"],
    )
    op.create_index(
        "ix_clinical_order_items_laboratory_test_id",
        "clinical_order_items",
        ["laboratory_test_id"],
    )
    op.create_index(
        "ix_clinical_order_items_status",
        "clinical_order_items",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_clinical_order_items_status",
        table_name="clinical_order_items",
    )
    op.drop_index(
        "ix_clinical_order_items_laboratory_test_id",
        table_name="clinical_order_items",
    )
    op.drop_index(
        "ix_clinical_order_items_item_type",
        table_name="clinical_order_items",
    )
    op.drop_index(
        "ix_clinical_order_items_diagnostic_investigation_id",
        table_name="clinical_order_items",
    )
    op.drop_index(
        "ix_clinical_order_items_clinical_order_id",
        table_name="clinical_order_items",
    )

    op.drop_table("clinical_order_items")

    clinical_order_item_status_enum.drop(op.get_bind(), checkfirst=True)
    clinical_order_item_type_enum.drop(op.get_bind(), checkfirst=True)
