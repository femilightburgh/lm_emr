"""
make episode numbers unique per hospital

Revision ID: 43d1a492c57a
Revises: d191471893fa
Create Date: 2026-08-08 03:29:10.189192
"""

from typing import Sequence, Union

from alembic import op


# Revision identifiers, used by Alembic.
revision: str = "43d1a492c57a"
down_revision: Union[str, Sequence[str], None] = "d191471893fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Change Episode number uniqueness from global to hospital-scoped.
    """

    # ------------------------------------------------------------------
    # Remove the existing globally unique index
    # ------------------------------------------------------------------

    op.drop_index(
        "ix_episodes_episode_number",
        table_name="episodes",
    )

    # ------------------------------------------------------------------
    # Recreate the normal index
    # ------------------------------------------------------------------

    op.create_index(
        "ix_episodes_episode_number",
        "episodes",
        ["episode_number"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # Add hospital-scoped uniqueness
    # ------------------------------------------------------------------

    op.create_unique_constraint(
        "uq_episodes_hospital_episode_number",
        "episodes",
        ["hospital_id", "episode_number"],
    )


def downgrade() -> None:
    """
    Restore global Episode number uniqueness.
    """

    # ------------------------------------------------------------------
    # Remove hospital-scoped uniqueness
    # ------------------------------------------------------------------

    op.drop_constraint(
        "uq_episodes_hospital_episode_number",
        "episodes",
        type_="unique",
    )

    # ------------------------------------------------------------------
    # Remove normal index
    # ------------------------------------------------------------------

    op.drop_index(
        "ix_episodes_episode_number",
        table_name="episodes",
    )

    # ------------------------------------------------------------------
    # Restore globally unique index
    # ------------------------------------------------------------------

    op.create_index(
        "ix_episodes_episode_number",
        "episodes",
        ["episode_number"],
        unique=True,
    )