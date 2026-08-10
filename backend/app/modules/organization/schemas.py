"""
==============================================================================
LIGHTBURGH EMR

Organization Schemas

==============================================================================

Pydantic schemas for Organization requests and responses.

==============================================================================
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.organization.enums import (
    DepartmentCategory,
    DepartmentStatus,
    HospitalOwnership,
    HospitalType,
)


class HospitalCreate(BaseModel):
    """
    Request payload for creating a hospital.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    code: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Unique hospital code.",
    )

    hospital_type: HospitalType

    ownership: HospitalOwnership

    email: EmailStr

    phone: str = Field(
        ...,
        max_length=30,
    )

    website: str | None = None

    address: str = Field(
        ...,
        max_length=500,
    )

    city: str = Field(
        ...,
        max_length=100,
    )

    state: str = Field(
        ...,
        max_length=100,
    )

    country: str = "Nigeria"

    timezone: str = "Africa/Lagos"

    logo_url: str | None = None

    license_number: str | None = None


class HospitalResponse(BaseModel):
    """
    Response returned after creating a hospital.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str

    code: str

    hospital_type: HospitalType

    ownership: HospitalOwnership

    email: EmailStr

    phone: str

    website: str | None

    address: str

    city: str

    state: str

    country: str

    timezone: str

    logo_url: str | None

    license_number: str | None


class DepartmentCreate(BaseModel):
    """
    Request payload for creating a hospital department.

    Department codes are unique within a hospital.
    """

    hospital_id: UUID

    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique department code within the hospital.",
    )

    category: DepartmentCategory

    status: DepartmentStatus = DepartmentStatus.ACTIVE


class DepartmentResponse(BaseModel):
    """
    Response returned for a hospital department.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hospital_id: UUID
    name: str
    code: str
    category: DepartmentCategory
    status: DepartmentStatus


class DepartmentUpdate(BaseModel):
    """
    Request payload for updating a hospital department.

    All fields are optional to support partial updates.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    category: DepartmentCategory | None = None

    status: DepartmentStatus | None = None