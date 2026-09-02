"""
==============================================================================
LIGHTBURGH EMR

Add Inpatient Medication Treatment and Administration
==============================================================================
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "73bc5a2d4ab0"
down_revision: Union[str, Sequence[str], None] = "b2d7f17ac8a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    medication_treatment_status = sa.Enum(
        "ACTIVE",
        "DISCONTINUED",
        "COMPLETED",
        name="medication_treatment_status_enum",
    )

    medication_dose_status = sa.Enum(
        "PENDING",
        "DUE",
        "GIVEN",
        "HELD",
        "MISSED",
        "CANCELLED",
        name="medication_dose_status_enum",
    )

    medication_administration_status = sa.Enum(
        "GIVEN",
        "HELD",
        "MISSED",
        "REFUSED",
        name="medication_administration_status_enum",
    )

    op.create_table(
        "medication_treatments",

        sa.Column(
            "prescription_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "episode_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "status",
            medication_treatment_status,
            nullable=False,
            server_default="ACTIVE",
        ),

        sa.Column(
            "start_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "end_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "discontinued_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "discontinued_by",
            sa.UUID(),
            nullable=True,
        ),

        sa.Column(
            "discontinued_reason",
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
            ["prescription_id"],
            ["prescriptions.id"],
        ),

        sa.ForeignKeyConstraint(
            ["episode_id"],
            ["episodes.id"],
        ),

        sa.ForeignKeyConstraint(
            ["discontinued_by"],
            ["staff.id"],
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "prescription_id",
            name="uq_medication_treatment_prescription",
        ),
    )

    op.create_index(
        "ix_medication_treatments_episode_id",
        "medication_treatments",
        ["episode_id"],
        unique=False,
    )

    op.create_index(
        "ix_medication_treatments_prescription_id",
        "medication_treatments",
        ["prescription_id"],
        unique=True,
    )

    op.create_index(
        "ix_medication_treatments_status",
        "medication_treatments",
        ["status"],
        unique=False,
    )

    op.create_table(
        "medication_doses",

        sa.Column(
            "treatment_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "status",
            medication_dose_status,
            nullable=False,
            server_default="PENDING",
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
            ["treatment_id"],
            ["medication_treatments.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "treatment_id",
            "scheduled_at",
            name="uq_medication_dose_treatment_time",
        ),
    )

    op.create_index(
        "ix_medication_doses_treatment_id",
        "medication_doses",
        ["treatment_id"],
        unique=False,
    )

    op.create_index(
        "ix_medication_doses_scheduled_at",
        "medication_doses",
        ["scheduled_at"],
        unique=False,
    )

    op.create_index(
        "ix_medication_doses_status",
        "medication_doses",
        ["status"],
        unique=False,
    )

    op.create_table(
        "medication_administrations",

        sa.Column(
            "dose_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "administered_by",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "status",
            medication_administration_status,
            nullable=False,
        ),

        sa.Column(
            "administered_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "dose_given",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "reason",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "notes",
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
            ["dose_id"],
            ["medication_doses.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["administered_by"],
            ["staff.id"],
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_medication_administrations_dose_id",
        "medication_administrations",
        ["dose_id"],
        unique=False,
    )

    op.create_index(
        "ix_medication_administrations_administered_by",
        "medication_administrations",
        ["administered_by"],
        unique=False,
    )

    op.create_index(
        "ix_medication_administrations_status",
        "medication_administrations",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_medication_administrations_status",
        table_name="medication_administrations",
    )

    op.drop_index(
        "ix_medication_administrations_administered_by",
        table_name="medication_administrations",
    )

    op.drop_index(
        "ix_medication_administrations_dose_id",
        table_name="medication_administrations",
    )

    op.drop_table("medication_administrations")

    op.drop_index(
        "ix_medication_doses_status",
        table_name="medication_doses",
    )

    op.drop_index(
        "ix_medication_doses_scheduled_at",
        table_name="medication_doses",
    )

    op.drop_index(
        "ix_medication_doses_treatment_id",
        table_name="medication_doses",
    )

    op.drop_table("medication_doses")

    op.drop_index(
        "ix_medication_treatments_status",
        table_name="medication_treatments",
    )

    op.drop_index(
        "ix_medication_treatments_prescription_id",
        table_name="medication_treatments",
    )

    op.drop_index(
        "ix_medication_treatments_episode_id",
        table_name="medication_treatments",
    )

    op.drop_table("medication_treatments")

    bind = op.get_bind()

    sa.Enum(
        "GIVEN",
        "HELD",
        "MISSED",
        "REFUSED",
        name="medication_administration_status_enum",
    ).drop(
        bind,
        checkfirst=True,
    )

    sa.Enum(
        "PENDING",
        "DUE",
        "GIVEN",
        "HELD",
        "MISSED",
        "CANCELLED",
        name="medication_dose_status_enum",
    ).drop(
        bind,
        checkfirst=True,
    )

    sa.Enum(
        "ACTIVE",
        "DISCONTINUED",
        "COMPLETED",
        name="medication_treatment_status_enum",
    ).drop(
        bind,
        checkfirst=True,
    )

