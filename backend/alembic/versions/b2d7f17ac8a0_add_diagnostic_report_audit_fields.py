"""
add diagnostic report audit fields

Revision ID: b2d7f17ac8a0
Revises: ec11d6974b57
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2d7f17ac8a0"
down_revision: Union[str, Sequence[str], None] = "ec11d6974b57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "diagnostic_reports",
        sa.Column(
            "reported_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "diagnostic_reports",
        sa.Column(
            "recorded_by",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "diagnostic_reports",
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_diagnostic_reports_recorded_by"),
        "diagnostic_reports",
        ["recorded_by"],
        unique=False,
    )

    op.create_foreign_key(
        op.f("fk_diagnostic_reports_recorded_by_staff"),
        "diagnostic_reports",
        "staff",
        ["recorded_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_diagnostic_reports_recorded_by_staff"),
        "diagnostic_reports",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_diagnostic_reports_recorded_by"),
        table_name="diagnostic_reports",
    )

    op.drop_column(
        "diagnostic_reports",
        "recorded_at",
    )

    op.drop_column(
        "diagnostic_reports",
        "recorded_by",
    )

    op.drop_column(
        "diagnostic_reports",
        "reported_at",
    )
