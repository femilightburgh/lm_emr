"""
==============================================================================
LIGHTBURGH EMR

Staff Models

==============================================================================

This module defines the Staff entity.

A Staff member represents an individual employed by a hospital.
Staff records are separate from authentication accounts
(UserAccount) because not every employee requires access to
the EMR.

==============================================================================
"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity

from .enums import (
    EmploymentStatus,
    EmploymentType,
    Gender,
    Profession,
)

if TYPE_CHECKING:
    from app.modules.identity.models import UserAccount
    from app.modules.organization.models import Hospital


class Staff(BaseEntity):
    """
    Represents a hospital employee.

    This model stores demographic and employment information
    for all staff members, regardless of whether they have
    a UserAccount.
    """

    __tablename__ = "staff"

    # ------------------------------------------------------------------
    # Table Constraints
    # ------------------------------------------------------------------

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "staff_number",
            name="uq_staff_hospital_staff_number",
        ),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    hospital_id: Mapped[str] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
    )

    user_account_id: Mapped[str | None] = mapped_column(
        ForeignKey("user_accounts.id"),
        nullable=True,
        unique=True,
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    staff_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    middle_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    gender: Mapped[Gender] = mapped_column(
        Enum(
            Gender,
            name="staff_gender_enum",
        ),
        nullable=False,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
    )

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ------------------------------------------------------------------
    # Employment
    # ------------------------------------------------------------------

    profession: Mapped[Profession] = mapped_column(
        Enum(
            Profession,
            name="staff_profession_enum",
        ),
        nullable=False,
    )

    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(
            EmploymentStatus,
            name="employment_status_enum",
        ),
        nullable=False,
        default=EmploymentStatus.ACTIVE,
    )

    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(
            EmploymentType,
            name="employment_type_enum",
        ),
        nullable=False,
    )

    date_employed: Mapped[date | None] = mapped_column(
        Date,
    )

    date_left: Mapped[date | None] = mapped_column(
        Date,
    )

    # ------------------------------------------------------------------
    # ORM Relationships
    # ------------------------------------------------------------------

    hospital: Mapped["Hospital"] = relationship(
        back_populates="staff_members",
    )

    user_account: Mapped["UserAccount | None"] = relationship(
        back_populates="staff_profile",
    )