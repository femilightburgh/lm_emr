"""
add episode patient flow

Revision ID: df6613f4f9ae
Revises: 9d322d4851a1
Create Date: 2026-08-16 17:47:16.964992
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "df6613f4f9ae"
down_revision: Union[str, Sequence[str], None] = "9d322d4851a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ============================================================================
# Constants
# ============================================================================

EPISODE_FLOW_STATUS_ENUM = "episode_flow_status_enum"


def upgrade() -> None:
    """
    Add operational patient-flow fields to Episodes.

    Existing Episodes are placed into AWAITING_CHECK_IN so that the
    migration is safe for databases that already contain Episode records.
    """

    # ------------------------------------------------------------------
    # Create Episode Flow Status enum
    # ------------------------------------------------------------------

    episode_flow_status_enum = postgresql.ENUM(
        "AWAITING_CHECK_IN",
        "WAITING_FOR_NURSING",
        "NURSING_IN_PROGRESS",
        "ROUTED",
        name=EPISODE_FLOW_STATUS_ENUM,
    )

    episode_flow_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # ------------------------------------------------------------------
    # Add flow status temporarily as nullable
    # ------------------------------------------------------------------

    op.add_column(
        "episodes",
        sa.Column(
            "flow_status",
            postgresql.ENUM(
                "AWAITING_CHECK_IN",
                "WAITING_FOR_NURSING",
                "NURSING_IN_PROGRESS",
                "ROUTED",
                name=EPISODE_FLOW_STATUS_ENUM,
                create_type=False,
            ),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # Add operational timestamps
    # ------------------------------------------------------------------

    op.add_column(
        "episodes",
        sa.Column(
            "checked_in_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "episodes",
        sa.Column(
            "triaged_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "episodes",
        sa.Column(
            "routed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # Add workflow staff references
    # ------------------------------------------------------------------

    op.add_column(
        "episodes",
        sa.Column(
            "checked_in_by",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "episodes",
        sa.Column(
            "triaged_by",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "episodes",
        sa.Column(
            "routed_by",
            sa.UUID(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # Add current routing destination
    # ------------------------------------------------------------------

    op.add_column(
        "episodes",
        sa.Column(
            "current_department_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # Backfill existing Episodes
    # ------------------------------------------------------------------

    op.execute(
        sa.text(
            """
            UPDATE episodes
            SET flow_status = 'AWAITING_CHECK_IN'
            WHERE flow_status IS NULL
            """
        )
    )

    # ------------------------------------------------------------------
    # Make flow status mandatory
    # ------------------------------------------------------------------

    op.alter_column(
        "episodes",
        "flow_status",
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------

    op.create_index(
        "ix_episodes_flow_status",
        "episodes",
        ["flow_status"],
        unique=False,
    )

    op.create_index(
        "ix_episodes_checked_in_by",
        "episodes",
        ["checked_in_by"],
        unique=False,
    )

    op.create_index(
        "ix_episodes_triaged_by",
        "episodes",
        ["triaged_by"],
        unique=False,
    )

    op.create_index(
        "ix_episodes_routed_by",
        "episodes",
        ["routed_by"],
        unique=False,
    )

    op.create_index(
        "ix_episodes_current_department_id",
        "episodes",
        ["current_department_id"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # Foreign keys
    # ------------------------------------------------------------------

    op.create_foreign_key(
        "fk_episodes_checked_in_by_staff",
        "episodes",
        "staff",
        ["checked_in_by"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_episodes_triaged_by_staff",
        "episodes",
        "staff",
        ["triaged_by"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_episodes_routed_by_staff",
        "episodes",
        "staff",
        ["routed_by"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_episodes_current_department",
        "episodes",
        "departments",
        ["current_department_id"],
        ["id"],
    )


def downgrade() -> None:
    """
    Remove Episode operational patient-flow fields.
    """

    # ------------------------------------------------------------------
    # Foreign keys
    # ------------------------------------------------------------------

    op.drop_constraint(
        "fk_episodes_current_department",
        "episodes",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_episodes_routed_by_staff",
        "episodes",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_episodes_triaged_by_staff",
        "episodes",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_episodes_checked_in_by_staff",
        "episodes",
        type_="foreignkey",
    )

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------

    op.drop_index(
        "ix_episodes_current_department_id",
        table_name="episodes",
    )

    op.drop_index(
        "ix_episodes_routed_by",
        table_name="episodes",
    )

    op.drop_index(
        "ix_episodes_triaged_by",
        table_name="episodes",
    )

    op.drop_index(
        "ix_episodes_checked_in_by",
        table_name="episodes",
    )

    op.drop_index(
        "ix_episodes_flow_status",
        table_name="episodes",
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    op.drop_column(
        "episodes",
        "current_department_id",
    )

    op.drop_column(
        "episodes",
        "routed_by",
    )

    op.drop_column(
        "episodes",
        "triaged_by",
    )

    op.drop_column(
        "episodes",
        "checked_in_by",
    )

    op.drop_column(
        "episodes",
        "routed_at",
    )

    op.drop_column(
        "episodes",
        "triaged_at",
    )

    op.drop_column(
        "episodes",
        "checked_in_at",
    )

    op.drop_column(
        "episodes",
        "flow_status",
    )

    # ------------------------------------------------------------------
    # Enum
    # ------------------------------------------------------------------

    episode_flow_status_enum = postgresql.ENUM(
        "AWAITING_CHECK_IN",
        "WAITING_FOR_NURSING",
        "NURSING_IN_PROGRESS",
        "ROUTED",
        name=EPISODE_FLOW_STATUS_ENUM,
    )

    episode_flow_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )