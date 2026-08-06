"""
========================================================================

LIGHTBURGH EMR

Authorization API Router

========================================================================

Purpose
-------

Administrative endpoints for roles and permissions.

Authentication endpoints belong in router.py.

Business logic belongs in services.

Database access belongs in repositories.

========================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.security.authorization import require_role

from app.modules.identity.permission_repository import (
    PermissionRepository,
)
from app.modules.identity.role_permission_repository import (
    RolePermissionRepository,
)
from app.modules.identity.role_permission_service import (
    RolePermissionService,
)
from app.modules.identity.schemas import (
    AssignPermissionRequest,
    PermissionResponse,
    RolePermissionsResponse,
)

router = APIRouter(
    prefix="/authorization",
    tags=["Authorization"],
)


@router.post(
    "/roles/{role_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign permission to role",
)
def assign_permission(
    role_id: UUID,
    request: AssignPermissionRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("Administrator")),
):
    """
    Assign a platform permission to a role.
    """

    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    service.assign_permission(
        role_id=role_id,
        permission_code=request.permission_code,
    )

    db.commit()


@router.get(
    "/roles/{role_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="List role permissions",
)
def list_permissions(
    role_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_role("Administrator")),
):
    """
    Return all permissions assigned to a role.
    """

    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    permissions = service.list_permissions(
        role_id=role_id,
    )

    return RolePermissionsResponse(
        permissions=[
            PermissionResponse.model_validate(permission)
            for permission in permissions
        ]
    )


@router.delete(
    "/roles/{role_id}/permissions/{permission_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove permission from role",
)
def remove_permission(
    role_id: UUID,
    permission_code: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("Administrator")),
):
    """
    Remove a permission from a role.
    """

    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    service.remove_permission(
        role_id=role_id,
        permission_code=permission_code,
    )

    db.commit()