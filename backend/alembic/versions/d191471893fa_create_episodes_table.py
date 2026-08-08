"""create episodes table

Revision ID: d191471893fa
Revises: f7c349a3a9aa
Create Date: 2026-08-08 00:01:07.946866
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = "d191471893fa"
down_revision: Union[str, Sequence[str], None] = "f7c349a3a9aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema.
    """

    # ------------------------------------------------------------------
    # Episodes
    # ------------------------------------------------------------------

    op.create_table(
        "episodes",

        sa.Column(
            "hospital_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "patient_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "episode_number",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "OPEN",
                "CLOSED",
                "CANCELLED",
                name="episode_status_enum",
            ),
            nullable=False,
        ),

        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
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
            ["hospital_id"],
            ["hospitals.id"],
        ),

        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        op.f("ix_episodes_episode_number"),
        "episodes",
        ["episode_number"],
        unique=True,
    )

    op.create_index(
        op.f("ix_episodes_hospital_id"),
        "episodes",
        ["hospital_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_episodes_patient_id"),
        "episodes",
        ["patient_id"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------

    op.add_column(
        "patients",
        sa.Column(
            "hospital_id",
            sa.UUID(),
            nullable=False,
        ),
    )

    op.create_index(
        op.f("ix_patients_hospital_id"),
        "patients",
        ["hospital_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_patients_hospital_id",
        "patients",
        "hospitals",
        ["hospital_id"],
        ["id"],
    )


def downgrade() -> None:
    """
    Downgrade schema.
    """

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------

    op.drop_constraint(
        "fk_patients_hospital_id",
        "patients",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_patients_hospital_id"),
        table_name="patients",
    )

    op.drop_column(
        "patients",
        "hospital_id",
    )

    # ------------------------------------------------------------------
    # Episodes
    # ------------------------------------------------------------------

    op.drop_index(
        op.f("ix_episodes_patient_id"),
        table_name="episodes",
    )

    op.drop_index(
        op.f("ix_episodes_hospital_id"),
        table_name="episodes",
    )

    op.drop_index(
        op.f("ix_episodes_episode_number"),
        table_name="episodes",
    )

    op.drop_table(
        "episodes",
    )