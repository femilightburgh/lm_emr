"""
==============================================================================
LIGHTBURGH EMR

Staff Router
==============================================================================

API endpoints for managing staff members.

The router is responsible only for handling HTTP requests and responses.
Business logic is delegated to the StaffService.
==============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.staff.dependencies import get_staff_service
from app.modules.staff.schemas import (
    StaffCreate,
    StaffListResponse,
    StaffResponse,
    StaffUpdate,
)
from app.modules.staff.service import StaffService

router = APIRouter(
    prefix="/staff",
    tags=["Staff"],
)


@router.post(
    "",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new staff member",
)
def create_staff(
    payload: StaffCreate,
    service: StaffService = Depends(get_staff_service),
) -> StaffResponse:
    """
    Register a new staff member.
    """

    staff = service.create_staff(payload)

    return StaffResponse.model_validate(staff)


@router.get(
    "/{staff_id}",
    response_model=StaffResponse,
    summary="Retrieve a staff member",
)
def get_staff(
    staff_id: UUID,
    service: StaffService = Depends(get_staff_service),
) -> StaffResponse:
    """
    Retrieve a staff member by ID.
    """

    staff = service.get_staff(staff_id)

    return StaffResponse.model_validate(staff)


@router.get(
    "",
    response_model=StaffListResponse,
    summary="List hospital staff",
)
def list_staff(
    hospital_id: UUID,
    service: StaffService = Depends(get_staff_service),
) -> StaffListResponse:
    """
    Retrieve all staff members belonging to a hospital.
    """

    staff = service.list_staff(hospital_id)

    return StaffListResponse(
        items=[
            StaffResponse.model_validate(member)
            for member in staff
        ],
        total=len(staff),
    )


@router.put(
    "/{staff_id}",
    response_model=StaffResponse,
    summary="Update a staff member",
)
def update_staff(
    staff_id: UUID,
    payload: StaffUpdate,
    service: StaffService = Depends(get_staff_service),
) -> StaffResponse:
    """
    Update an existing staff member.
    """

    staff = service.update_staff(
        staff_id=staff_id,
        data=payload,
    )

    return StaffResponse.model_validate(staff)