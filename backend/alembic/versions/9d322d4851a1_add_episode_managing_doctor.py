"""
==============================================================================
LIGHTBURGH EMR

Add Episode Managing Doctor

==============================================================================

Adds the managing doctor relationship to Episodes of Care.

An Episode may have no managing doctor while OPEN.

When an Episode is admitted, the admitting doctor becomes the
managing doctor.

==============================================================================
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d322d4851a1"
down_revision: Union[str, Sequence[str], None] = "9e101b235439"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add managing doctor to Episodes.
    """

    # ------------------------------------------------------------------
    # Managing Doctor
    # ------------------------------------------------------------------

    op.add_column(
        "episodes",
        sa.Column(
            "managing_doctor_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # Index
    # ------------------------------------------------------------------

    op.create_index(
        "ix_episodes_managing_doctor_id",
        "episodes",
        ["managing_doctor_id"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # Foreign Key
    # ------------------------------------------------------------------

    op.create_foreign_key(
        "fk_episodes_managing_doctor_id_staff",
        "episodes",
        "staff",
        ["managing_doctor_id"],
        ["id"],
    )


def downgrade() -> None:
    """
    Remove the managing doctor relationship from Episodes.
    """

    # ------------------------------------------------------------------
    # Foreign Key
    # ------------------------------------------------------------------

    op.drop_constraint(
        "fk_episodes_managing_doctor_id_staff",
        "episodes",
        type_="foreignkey",
    )

    # ------------------------------------------------------------------
    # Index
    # ------------------------------------------------------------------

    op.drop_index(
        "ix_episodes_managing_doctor_id",
        table_name="episodes",
    )

    # ------------------------------------------------------------------
    # Column
    # ------------------------------------------------------------------

    op.drop_column(
        "episodes",
        "managing_doctor_id",
    )