"""
==============================================================================
LIGHTBURGH EMR

Organization Models

==============================================================================

This module contains ORM models representing healthcare organizations.

The Hospital model is the root entity for LIGHTBURGH's multi-tenant
architecture.

Every business entity—including staff, patients, appointments,
laboratory results, pharmacy orders, and billing records—belongs
to exactly one hospital.

Responsibilities
----------------
• Store hospital profile information.
• Support multi-tenancy.
• Own user accounts.
• Own staff members.
• Own roles and permissions.

==============================================================================
"""

from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)

if TYPE_CHECKING:
    from app.modules.identity.models import Role, UserAccount
    from app.modules.staff.models import Staff


class Hospital(BaseEntity):
    """
    Represents a healthcare organization.

    Every clinical and administrative record belongs to exactly
    one hospital, making this the root aggregate for multi-tenancy.
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

    user_accounts: Mapped[list["UserAccount"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    roles: Mapped[list["Role"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    staff_members: Mapped[list["Staff"]] = relationship(
        back_populates="hospital",
        cascade="all, delete-orphan",
    )