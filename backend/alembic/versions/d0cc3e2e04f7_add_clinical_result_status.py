"""add clinical result status

Revision ID: d0cc3e2e04f7
Revises: 2939eeaa93fb
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d0cc3e2e04f7"
down_revision: Union[str, Sequence[str], None] = "2939eeaa93fb"
branch_labels = None
depends_on = None


RESULT_STATUS_ENUM = "clinical_result_status_enum"


def upgrade() -> None:
    result_status_enum = postgresql.ENUM(
        "DRAFT",
        "FINAL",
        name=RESULT_STATUS_ENUM,
    )

    result_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "clinical_results",
        sa.Column(
            "status",
            postgresql.ENUM(
                "DRAFT",
                "FINAL",
                name=RESULT_STATUS_ENUM,
                create_type=False,
            ),
            nullable=False,
            server_default="FINAL",
        ),
    )

    op.alter_column(
        "clinical_results",
        "status",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "clinical_results",
        "status",
    )

    result_status_enum = postgresql.ENUM(
        "DRAFT",
        "FINAL",
        name=RESULT_STATUS_ENUM,
    )

    result_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
