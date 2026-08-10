"""
LIGHTBURGH EMR

Department Router

===============================================================================

API endpoints for managing hospital departments.

Departments are hospital-scoped organizational entities.
Historical departments are retained and can be marked inactive.

Authorization
-------------
department.read
    Retrieve departments.

department.create
    Create departments.

===============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from app.core.security.authorization import require_permission
from app.modules.identity.permissions import Permissions
from app.modules.organization.department_dependencies import (
    get_department_service,
)
from app.modules.organization.department_service import DepartmentService
from app.modules.organization.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a hospital department",
    description=(
        "Create a department belonging to a hospital. "
        "Requires the department.create permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.DEPARTMENT_CREATE)),
    ],
)
def create_department(
    payload: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    """
    Create a hospital department.

    Requires:
        department.create
    """

    department = service.create_department(payload)

    return DepartmentResponse.model_validate(department)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Retrieve a department",
    description=(
        "Retrieve a department by ID. "
        "Requires the department.read permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.DEPARTMENT_READ)),
    ],
)
def get_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    """
    Retrieve a department by ID.

    Requires:
        department.read
    """

    department = service.get_department(department_id)

    return DepartmentResponse.model_validate(department)


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Update a department",
    description=(
        "Update an existing hospital department. "
        "Requires the department.update permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.DEPARTMENT_UPDATE)),
    ],
)
def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    """
    Update an existing department.

    Requires:
        department.update
    """

    department = service.update_department(
        department_id=department_id,
        data=payload,
    )

    return DepartmentResponse.model_validate(department)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a department",
    description=(
        "Delete an existing hospital department. "
        "Requires the department.delete permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.DEPARTMENT_DELETE)),
    ],
)
def delete_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
) -> None:
    """
    Delete an existing department.

    Requires:
        department.delete
    """

    service.delete_department(department_id)


@router.get(
    "",
    response_model=list[DepartmentResponse],
    summary="List hospital departments",
    description=(
        "Retrieve departments belonging to a hospital. "
        "Requires the department.read permission."
    ),
    dependencies=[
        Depends(require_permission(Permissions.DEPARTMENT_READ)),
    ],
)
def list_departments(
    hospital_id: UUID,
    service: DepartmentService = Depends(get_department_service),
) -> list[DepartmentResponse]:
    """
    List departments belonging to a hospital.

    Requires:
        department.read
    """

    departments = service.list_departments(hospital_id)

    return [
        DepartmentResponse.model_validate(department)
        for department in departments
    ]