"""
create clinical results

Revision ID: bd801cdac8fa
Revises: 9380978c1f1b
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "bd801cdac8fa"
down_revision: Union[str, Sequence[str], None] = "9380978c1f1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CLINICAL_RESULT_TYPE_ENUM = "clinical_result_type_enum"


def upgrade() -> None:
    result_type_enum = postgresql.ENUM(
        "LABORATORY",
        "RADIOLOGY",
        name=CLINICAL_RESULT_TYPE_ENUM,
    )

    result_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "clinical_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "result_type",
            postgresql.ENUM(
                "LABORATORY",
                "RADIOLOGY",
                name=CLINICAL_RESULT_TYPE_ENUM,
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "result_data",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "recorded_by",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
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
            ["order_id"],
            ["clinical_orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by"],
            ["staff.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_clinical_results_order_id",
        "clinical_results",
        ["order_id"],
    )

    op.create_index(
        "ix_clinical_results_result_type",
        "clinical_results",
        ["result_type"],
    )

    op.create_index(
        "ix_clinical_results_recorded_by",
        "clinical_results",
        ["recorded_by"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_clinical_results_recorded_by",
        table_name="clinical_results",
    )

    op.drop_index(
        "ix_clinical_results_result_type",
        table_name="clinical_results",
    )

    op.drop_index(
        "ix_clinical_results_order_id",
        table_name="clinical_results",
    )

    op.drop_table("clinical_results")

    result_type_enum = postgresql.ENUM(
        "LABORATORY",
        "RADIOLOGY",
        name=CLINICAL_RESULT_TYPE_ENUM,
    )

    result_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
