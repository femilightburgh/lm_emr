"""
==============================================================================
LIGHTBURGH EMR

Organization Models

==============================================================================

This module contains ORM models representing healthcare organizations.

The Hospital model is the root aggregate of LIGHTBURGH's multi-tenant
architecture.

Every business entity—including patients, staff, user accounts, Episodes of
Care, Clinical Events, laboratory requests, radiology studies, pharmacy
dispensing, billing records and future modules—belongs to exactly one
hospital.

Responsibilities
----------------
• Store hospital profile information.
• Support multi-tenancy.
• Own patient records.
• Own staff members.
• Own user accounts.
• Own roles.

==============================================================================
"""

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.organization.enums import (
    DepartmentCategory,
    DepartmentStatus,
    HospitalOwnership,
    HospitalType,
)
from app.modules.episode.models import Episode
from app.modules.patients.models import Patient

if TYPE_CHECKING:
    from app.modules.identity.models import Role, UserAccount
    from app.modules.patients.models import Patient
    from app.modules.staff.models import Staff
    from app.modules.laboratory.models import LaboratoryTest


class Hospital(BaseEntity):
    """
    Represents a healthcare organization.

    Every clinical and administrative record belongs to exactly one
    hospital, making Hospital the root aggregate for LIGHTBURGH's
    multi-tenant architecture.
    """

    __tablename__ = "hospitals"

    # ------------------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    hospital_type: Mapped[HospitalType] = mapped_column(
        Enum(
            HospitalType,
            name="hospital_type_enum",
        ),
        nullable=False,
    )

    ownership: Mapped[HospitalOwnership] = mapped_column(
        Enum(
            HospitalOwnership,
            name="hospital_ownership_enum",
        ),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Contact Information
    # ------------------------------------------------------------------

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Address Information
    # ------------------------------------------------------------------

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Nigeria",
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Africa/Lagos",
    )

    # ------------------------------------------------------------------
    # Regulatory Information
    # ------------------------------------------------------------------

    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    license_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    patients: Mapped[list["Patient"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    staff_members: Mapped[list["Staff"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    user_accounts: Mapped[list["UserAccount"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    roles: Mapped[list["Role"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    departments: Mapped[list["Department"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    laboratory_tests: Mapped[list["LaboratoryTest"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )


class Department(BaseEntity):
    """
    Represents an organizational department within a hospital.

    Departments belong to exactly one hospital. They are retained
    historically even when no longer operational, so historical
    staff
    assignments can continue to reference them.
    """

    __tablename__ = "departments"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "code",
            name="uq_department_hospital_code",
        ),
    )

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------

    hospital_id: Mapped[str] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    category: Mapped[DepartmentCategory] = mapped_column(
        Enum(
            DepartmentCategory,
            name="department_category_enum",
        ),
        nullable=False,
    )

    status: Mapped[DepartmentStatus] = mapped_column(
        Enum(
            DepartmentStatus,
            name="department_status_enum",
        ),
        nullable=False,
        default=DepartmentStatus.ACTIVE,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    hospital: Mapped["Hospital"] = relationship(
        back_populates="departments",
    )