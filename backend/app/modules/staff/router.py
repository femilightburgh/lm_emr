"""
LIGHTBURGH EMR

Staff Router
============

API endpoints for managing hospital staff members.

Responsibilities
----------------
• Register new staff members.
• Retrieve individual staff records.
• List staff members belonging to a hospital.
• Update existing staff records.
• Enforce staff-level authorization through platform permissions.

Authorization
-------------
Staff endpoints are protected using the canonical platform permissions:

• staff.read   → Retrieve and list staff.
• staff.create → Create staff.
• staff.update → Modify staff.

Business rules and database operations remain delegated to
StaffService and StaffRepository respectively.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security.authorization import require_permission
from app.modules.identity.permissions import Permissions
from app.modules.staff.dependencies import get_staff_service
from app.modules.staff.schemas import (
    StaffCreate,
    StaffEmploymentClose,
    StaffEmploymentCreate,
    StaffEmploymentResponse,
    StaffListResponse,
    StaffResponse,
    StaffUpdate,
)
from app.modules.staff.service import StaffService


router = APIRouter(
    prefix="/staff",
    tags=["Staff"],
)


# ============================================================================
# Create Staff
# ============================================================================

@router.post(
    "",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new staff member",
    description=(
        "Register a new staff member in a hospital. "
        "Requires the staff.create permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_CREATE)),
    ],
)
def create_staff(
    payload: StaffCreate,
    service: StaffService = Depends(get_staff_service),
) -> StaffResponse:
    """
    Register a new staff member.

    Authorization
    -------------
    Requires:
        staff.create

    Parameters
    ----------
    payload:
        Staff information including the hospital, staff number,
        personal details, employment information, and contact details.

    Business Logic
    --------------
    StaffService validates that:
        - The hospital exists.
        - The staff number is unique within the hospital.
        - Employment dates are valid.

    Returns
    -------
    StaffResponse:
        The newly created staff member.
    """

    staff = service.create_staff(payload)

    return StaffResponse.model_validate(staff)

# ============================================================================
# Retrieve Staff
# ============================================================================

@router.get(
    "/{staff_id}",
    response_model=StaffResponse,
    summary="Retrieve a staff member",
    description=(
        "Retrieve a staff member by ID. "
        "Requires the staff.read permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_READ)),
    ],
)
def get_staff(
    staff_id: UUID,
    service: StaffService = Depends(get_staff_service),
) -> StaffResponse:
    """
    Retrieve a staff member by ID.

    Authorization
    -------------
    Requires:
        staff.read

    Parameters
    ----------
    staff_id:
        UUID of the staff member to retrieve.

    Business Logic
    --------------
    StaffService retrieves the staff record and raises
    StaffNotFoundError when the record does not exist.

    Returns
    -------
    StaffResponse:
        The requested staff member.
    """

    staff = service.get_staff(staff_id)

    return StaffResponse.model_validate(staff)


# ============================================================================
# List Employment History
# ============================================================================

@router.get(
    "/{staff_id}/employments",
    response_model=list[StaffEmploymentResponse],
    summary="List staff employment history",
    description=(
        "Retrieve the complete employment history for a staff member. "
        "Requires the staff.read permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_READ)),
    ],
)
def list_employment_history(
    staff_id: UUID,
    service: StaffService = Depends(get_staff_service),
) -> list[StaffEmploymentResponse]:
    """
    Retrieve the complete employment history for a staff member.

    Authorization
    -------------
    Requires:
        staff.read

    Parameters
    ----------
    staff_id:
        UUID of the staff member whose employment history should be returned.

    Business Logic
    --------------
    StaffService retrieves the employment records and raises
    StaffNotFoundError when the record does not exist.

    Returns
    -------
    list[StaffEmploymentResponse]:
        A list of employment periods for the specified staff member.
    """

    employments = service.list_employment_history(staff_id)

    return [
        StaffEmploymentResponse.model_validate(employment)
        for employment in employments
    ]

# ============================================================================
# Current Employment
# ============================================================================

@router.get(
    "/{staff_id}/employments/current",
    response_model=StaffEmploymentResponse | None,
    summary="Get current staff employment",
    description=(
        "Retrieve the current employment record for a staff member. "
        "Requires the staff.read permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_READ)),
    ],
)
def get_current_employment(
    staff_id: UUID,
    service: StaffService = Depends(get_staff_service),
) -> StaffEmploymentResponse | None:
    """
    Retrieve the current employment period for a staff member.

    Requires:
        staff.read
    """

    employment = service.get_current_employment(staff_id)

    if employment is None:
        return None

    return StaffEmploymentResponse.model_validate(
        employment,
    )


# ============================================================================
# Start Employment
# ============================================================================

@router.post(
    "/{staff_id}/employments",
    response_model=StaffEmploymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start staff employment",
    description=(
        "Start a new employment period for a staff member. "
        "Requires the staff.update permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_UPDATE)),
    ],
)
def start_employment(
    staff_id: UUID,
    payload: StaffEmploymentCreate,
    service: StaffService = Depends(get_staff_service),
) -> StaffEmploymentResponse:
    """
    Start a new employment period for a staff member.

    Requires:
        staff.update
    """

    employment = service.start_employment(
        staff_id=staff_id,
        data=payload,
    )

    return StaffEmploymentResponse.model_validate(
        employment,
    )


# ============================================================================
# Close Current Employment
# ============================================================================

@router.patch(
    "/{staff_id}/employments/current",
    response_model=StaffEmploymentResponse,
    summary="Close current staff employment",
    description=(
        "Close the current employment period for a staff member. "
        "Requires the staff.update permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_UPDATE)),
    ],
)
def close_current_employment(
    staff_id: UUID,
    payload: StaffEmploymentClose,
    service: StaffService = Depends(get_staff_service),
) -> StaffEmploymentResponse:
    """
    Close the current employment period.

    Requires:
        staff.update
    """

    employment = service.close_current_employment(
        staff_id=staff_id,
        data=payload,
    )

    return StaffEmploymentResponse.model_validate(
        employment,
    )

# ============================================================================
# List Hospital Staff
# ============================================================================

@router.get(
    "",
    response_model=StaffListResponse,
    summary="List hospital staff",
    description=(
        "Retrieve all staff members belonging to a hospital. "
        "Requires the staff.read permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_READ)),
    ],
)
def list_staff(
    hospital_id: UUID,
    service: StaffService = Depends(get_staff_service),
) -> StaffListResponse:
    """
    Retrieve all staff members belonging to a hospital.

    Authorization
    -------------
    Requires:
        staff.read

    Parameters
    ----------
    hospital_id:
        UUID of the hospital whose staff members should be returned.

    Business Logic
    --------------
    StaffService validates that the hospital exists before retrieving
    its staff records.

    Returns
    -------
    StaffListResponse:
        A list of staff members belonging to the specified hospital
        together with the total number of records.
    """

    staff = service.list_staff(hospital_id)

    return StaffListResponse(
        items=[
            StaffResponse.model_validate(member)
            for member in staff
        ],
        total=len(staff),
    )

# ============================================================================
# Update Staff
# ============================================================================

@router.put(
    "/{staff_id}",
    response_model=StaffResponse,
    summary="Update a staff member",
    description=(
        "Update an existing staff member. "
        "Requires the staff.update permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.STAFF_UPDATE)),
    ],
)
def update_staff(
    staff_id: UUID,
    payload: StaffUpdate,
    service: StaffService = Depends(get_staff_service),
) -> StaffResponse:
    """
    Update an existing staff member.

    Authorization
    -------------
    Requires:
        staff.update

    Business Logic
    --------------
    StaffService retrieves the existing staff record, applies the
    supplied changes, validates employment dates, and persists the
    updated record.
    """

    staff = service.update_staff(
        staff_id=staff_id,
        data=payload,
    )

    return StaffResponse.model_validate(staff)