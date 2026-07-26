"""add hospital ownership

Revision ID: 3f30d3316592
Revises: 0a50cc711abc
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3f30d3316592"
down_revision: Union[str, Sequence[str], None] = "0a50cc711abc"
branch_labels = None
depends_on = None


hospital_ownership_enum = sa.Enum(
    "PUBLIC",
    "PRIVATE",
    "FAITH_BASED",
    "MILITARY",
    "UNIVERSITY",
    "NGO",
    name="hospital_ownership_enum",
)


def upgrade():

    # Create PostgreSQL enum first
    hospital_ownership_enum.create(op.get_bind(), checkfirst=True)

    # Then add the column
    op.add_column(
        "hospitals",
        sa.Column(
            "ownership",
            hospital_ownership_enum,
            nullable=False,
            server_default="PRIVATE",
        ),
    )

    # Remove default after existing rows have been populated
    op.alter_column(
        "hospitals",
        "ownership",
        server_default=None,
    )


def downgrade():

    op.drop_column("hospitals", "ownership")

    hospital_ownership_enum.drop(op.get_bind(), checkfirst=True)