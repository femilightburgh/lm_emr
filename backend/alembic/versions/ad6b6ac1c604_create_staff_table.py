"""
==============================================================================
LIGHTBURGH EMR

Migration: Create Staff Table

Revision ID: ad6b6ac1c604
Revises: 3f30d3316592

==============================================================================

Purpose
-------
Creates the Staff module.

The Staff module stores all employees belonging to a hospital.

Staff records are intentionally separated from UserAccount records.

This design allows:

    • Employees without login accounts.
    • Future HR functionality.
    • Cleaner authentication architecture.

Database Objects Created
------------------------
• PostgreSQL ENUM types
• staff table
• business indexes
• foreign keys
• one-to-one constraint with UserAccount

==============================================================================
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# ==============================================================================
# Revision Information
# ==============================================================================

revision: str = "ad6b6ac1c604"
down_revision: Union[str, Sequence[str], None] = "3f30d3316592"
branch_labels = None
depends_on = None


# ==============================================================================
# PostgreSQL ENUM Types
#
# IMPORTANT:
#
# create_type=False prevents SQLAlchemy from trying to automatically create
# the ENUM when the table is created.
#
# We explicitly create the ENUM ourselves before creating the table.
# ==============================================================================

gender_enum = postgresql.ENUM(
    "MALE",
    "FEMALE",
    name="staff_gender_enum",
    create_type=False,
)

profession_enum = postgresql.ENUM(
    "DOCTOR",
    "NURSE",
    "PHARMACIST",
    "LABORATORY_SCIENTIST",
    "RADIOGRAPHER",
    "PHYSIOTHERAPIST",
    "DIETITIAN",
    "DENTIST",
    "RECEPTIONIST",
    "RECORDS_OFFICER",
    "ACCOUNTANT",
    "ADMINISTRATOR",
    "IT_SUPPORT",
    "OTHER",
    name="staff_profession_enum",
    create_type=False,
)

employment_status_enum = postgresql.ENUM(
    "ACTIVE",
    "ON_LEAVE",
    "SUSPENDED",
    "RESIGNED",
    "RETIRED",
    "TERMINATED",
    name="employment_status_enum",
    create_type=False,
)

employment_type_enum = postgresql.ENUM(
    "FULL_TIME",
    "PART_TIME",
    "CONTRACT",
    "LOCUM",
    "INTERN",
    "RESIDENT",
    "VISITING",
    name="employment_type_enum",
    create_type=False,
)


# ==============================================================================
# Upgrade
# ==============================================================================

def upgrade() -> None:
    """
    Apply the Staff module schema.
    """

    bind = op.get_bind()

    # --------------------------------------------------------------------------
    # Create ENUM Types
    # --------------------------------------------------------------------------

    gender_enum.create(bind, checkfirst=True)
    profession_enum.create(bind, checkfirst=True)
    employment_status_enum.create(bind, checkfirst=True)
    employment_type_enum.create(bind, checkfirst=True)

    # --------------------------------------------------------------------------
    # Create Staff Table
    # --------------------------------------------------------------------------

    op.create_table(
        "staff",

        # ------------------------------------------------------------------
        # Relationships
        # ------------------------------------------------------------------

        sa.Column(
            "hospital_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "user_account_id",
            sa.UUID(),
            nullable=True,
        ),

        # ------------------------------------------------------------------
        # Staff Identity
        # ------------------------------------------------------------------

        sa.Column(
            "staff_number",
            sa.String(50),
            nullable=False,
        ),

        sa.Column(
            "first_name",
            sa.String(100),
            nullable=False,
        ),

        sa.Column(
            "middle_name",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "last_name",
            sa.String(100),
            nullable=False,
        ),

        sa.Column(
            "gender",
            gender_enum,
            nullable=False,
        ),

        sa.Column(
            "date_of_birth",
            sa.Date(),
            nullable=True,
        ),

        # ------------------------------------------------------------------
        # Contact
        # ------------------------------------------------------------------

        sa.Column(
            "phone_number",
            sa.String(20),
            nullable=True,
        ),

        sa.Column(
            "email",
            sa.String(255),
            nullable=True,
        ),

        # ------------------------------------------------------------------
        # Employment
        # ------------------------------------------------------------------

        sa.Column(
            "profession",
            profession_enum,
            nullable=False,
        ),

        sa.Column(
            "employment_status",
            employment_status_enum,
            nullable=False,
        ),

        sa.Column(
            "employment_type",
            employment_type_enum,
            nullable=False,
        ),

        sa.Column(
            "date_employed",
            sa.Date(),
            nullable=True,
        ),

        sa.Column(
            "date_left",
            sa.Date(),
            nullable=True,
        ),

        # ------------------------------------------------------------------
        # BaseEntity Columns
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # Constraints
        # ------------------------------------------------------------------

        sa.PrimaryKeyConstraint(
            "id",
            name="pk_staff",
        ),

        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name="fk_staff_hospital",
        ),

        sa.ForeignKeyConstraint(
            ["user_account_id"],
            ["user_accounts.id"],
            name="fk_staff_user_account",
        ),

        sa.UniqueConstraint(
            "user_account_id",
            name="uq_staff_user_account",
        ),
    )

    # --------------------------------------------------------------------------
    # Business Indexes
    # --------------------------------------------------------------------------

    op.create_index(
        "ix_staff_staff_number",
        "staff",
        ["staff_number"],
        unique=True,
    )


# ==============================================================================
# Downgrade
# ==============================================================================

def downgrade() -> None:
    """
    Remove the Staff module.
    """

    bind = op.get_bind()

    # --------------------------------------------------------------------------
    # Drop Index
    # --------------------------------------------------------------------------

    op.drop_index(
        "ix_staff_staff_number",
        table_name="staff",
    )

    # --------------------------------------------------------------------------
    # Drop Table
    # --------------------------------------------------------------------------

    op.drop_table("staff")

    # --------------------------------------------------------------------------
    # Drop ENUM Types
    # --------------------------------------------------------------------------

    employment_type_enum.drop(bind, checkfirst=True)
    employment_status_enum.drop(bind, checkfirst=True)
    profession_enum.drop(bind, checkfirst=True)
    gender_enum.drop(bind, checkfirst=True)