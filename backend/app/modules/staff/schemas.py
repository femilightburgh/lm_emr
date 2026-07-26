"""
==============================================================================
LIGHTBURGH EMR

Staff API Schemas

==============================================================================

Purpose
-------
Defines the Pydantic schemas used by the Staff module.

Schemas represent the contract between the API layer and the business
service layer. They validate incoming requests and serialize outgoing
responses.

Responsibilities
----------------
• Validate incoming API requests.
• Serialize outgoing API responses.
• Prevent invalid payloads from reaching the business layer.
• Separate API contracts from SQLAlchemy ORM models.

Architecture
------------
                    HTTP Request
                          │
                          ▼
              StaffCreate / StaffUpdate
                          │
                          ▼
                    StaffService
                          │
                          ▼
                    Staff ORM Model
                          │
                          ▼
                     PostgreSQL

Notes
-----
Schemas perform structural validation only.

Business rules such as:

• Duplicate staff numbers
• Hospital existence
• Employment policies
• User account assignment

are enforced by the StaffService.

==============================================================================
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import EmailStr

from app.core.schemas import BaseSchema
from app.modules.staff.enums import (
    EmploymentStatus,
    EmploymentType,
    Gender,
    Profession,
)


# ==============================================================================
# Base Schema
# ==============================================================================


class StaffBase(BaseSchema):
    """
    Base schema shared by Staff request and response models.

    This schema defines the common staff attributes used throughout
    the Staff module.

    It is inherited by:

    • StaffCreate
    • StaffResponse

    Notes
    -----
    This schema should not be used directly as an API request or
    response model.
    """

    hospital_id: UUID

    staff_number: str

    first_name: str
    middle_name: str | None = None
    last_name: str

    gender: Gender

    date_of_birth: date

    phone_number: str | None = None

    email: EmailStr | None = None

    profession: Profession

    employment_status: EmploymentStatus

    employment_type: EmploymentType

    date_employed: date

    date_left: date | None = None


# ==============================================================================
# Create Schema
# ==============================================================================


class StaffCreate(StaffBase):
    """
    Request schema used when creating a new staff member.

    This schema represents the payload accepted by the Staff API when
    registering a new employee.

    Validation
    ----------
    Performs structural validation only.

    Business rules such as duplicate staff numbers, hospital existence,
    and employment policies are enforced by the StaffService.
    """

    pass


# ==============================================================================
# Update Schema
# ==============================================================================


class StaffUpdate(BaseSchema):
    """
    Request schema used when updating an existing staff member.

    All fields are optional to support partial updates (PATCH).

    Business rules are enforced by the StaffService.
    """

    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None

    gender: Gender | None = None

    date_of_birth: date | None = None

    phone_number: str | None = None

    email: EmailStr | None = None

    profession: Profession | None = None

    employment_status: EmploymentStatus | None = None

    employment_type: EmploymentType | None = None

    date_employed: date | None = None

    date_left: date | None = None


# ==============================================================================
# Response Schema
# ==============================================================================


class StaffResponse(StaffBase):
    """
    Response schema returned by the Staff API.

    In addition to the common staff attributes, this schema includes
    system-generated metadata.

    Returned by:

    • Create Staff
    • Retrieve Staff
    • Update Staff
    • List Staff
    """

    id: UUID

    user_account_id: UUID | None = None

    created_at: datetime

    updated_at: datetime

class StaffListResponse(BaseSchema):
    """
    Response schema representing a collection of staff members.

    This schema is returned by endpoints that list multiple staff
    records.
    """

    items: list[StaffResponse]
    total: int