"""
========================================================================

LIGHTBURGH EMR

Authorization API Router

========================================================================

Administrative endpoints for:

- Hospital users
- Hospital roles
- Role permissions
- User-role assignments

Authentication endpoints belong in router.py.

Business logic belongs in services.

Database access belongs in repositories.

HTTP concerns belong in this router.

========================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import RequestContext
from app.core.context import get_request_context
from app.core.security.authorization import require_role
from app.db.session import get_db

from app.modules.identity.exceptions import (
    PermissionNotFoundError,
    RoleAlreadyAssignedError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
    UserRoleNotFoundError,
    UserAlreadyExistsError,
)

from app.modules.identity.permission_repository import (
    PermissionRepository,
)

from app.modules.identity.repository import (
    IdentityRepository,
)

from app.modules.identity.role_permission_repository import (
    RolePermissionRepository,
)

from app.modules.identity.role_permission_service import (
    RolePermissionService,
)

from app.modules.identity.role_service import (
    RoleService,
)

from app.modules.identity.schemas import (
    AdminUserResponse,
    AssignPermissionRequest,
    AssignRoleRequest,
    CreateRoleRequest,
    PermissionResponse,
    RolePermissionsResponse,
    RoleResponse,
    UpdateRoleRequest,
    UserRoleResponse,
    CreateStaffRequest,
    CreateStaffResponse,
)

from app.modules.identity.user_service import (
    UserService,
)


router = APIRouter(
    prefix="/authorization",
    tags=["Authorization"],
)


# ============================================================================
# Internal Helpers
# ============================================================================


def _get_identity_repository(
    db: Session,
) -> IdentityRepository:
    """
    Build the IdentityRepository used by administrative services.
    """

    return IdentityRepository(db)


def _build_admin_user_response(
    user,
) -> AdminUserResponse:
    """
    Build the administrative representation of a user.

    Only active role assignments are exposed.

    Historical inactive UserRole records remain in the database
    but are intentionally excluded from the current role list.
    """

    roles = [
        UserRoleResponse(
            id=user_role.id,
            role_id=user_role.role_id,
            role_name=user_role.role.name,
            is_active=user_role.is_active,
        )
        for user_role in user.user_roles
        if user_role.is_active
    ]

    return AdminUserResponse(
        id=user.id,
        email=user.email,
        hospital_id=user.hospital_id,
        is_superuser=user.is_superuser,
        status=user.status,
        roles=roles,
    )


def _get_hospital_role_or_404(
    *,
    repository: IdentityRepository,
    context: RequestContext,
    role_id: UUID,
):
    """
    Retrieve a role while enforcing hospital tenancy.

    This helper is especially important for permission endpoints.

    A role UUID alone must never be sufficient for an administrator
    from one hospital to manipulate a role belonging to another
    hospital.
    """

    role = repository.get_role_by_id(
        hospital_id=context.hospital_id,
        role_id=role_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    return role


# ============================================================================
# Users
# ============================================================================
@router.post(
    "/users/onboard",
    response_model=CreateStaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard hospital staff",
)
def onboard_staff(
    request: CreateStaffRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Create a pending staff account and issue an activation invitation.

    The administrator supplies the staff member's email and
    initial role. The staff member establishes their password
    during activation.
    """

    repository = _get_identity_repository(db)

    service = UserService(
        repository=repository,
    )

    try:
        user, invitation_token, expires_at = (
            service.onboard_staff(
                hospital_id=context.hospital_id,
                email=request.email,
                role_name=request.role_name,
            )
        )

        db.commit()

        return CreateStaffResponse(
            user=_build_admin_user_response(user),
            invitation_token=invitation_token,
            invitation_expires_at=expires_at,
        )

    except RoleNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except RoleAlreadyAssignedError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except UserAlreadyExistsError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
    summary="List hospital users",
)
def list_users(
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Return all user accounts belonging to the authenticated Hospital.

    Only active role assignments are included in each user's
    current role list.
    """

    service = UserService(
        repository=_get_identity_repository(db),
    )

    users = service.list_users(
        context=context,
    )

    return [
        _build_admin_user_response(user)
        for user in users
    ]

@router.post(
    "/users/onboard",
    response_model=CreateStaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard hospital staff",
)
def onboard_staff(
    request: CreateStaffRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Create a pending staff account and issue an activation invitation.

    The administrator supplies the staff member's email and
    initial role. The staff member establishes their password
    during activation.
    """

    repository = _get_identity_repository(db)

    service = UserService(
        repository=repository,
    )

    try:
        user, invitation_token, expires_at = (
            service.onboard_staff(
                hospital_code=context.hospital_code,
                email=request.email,
                role_name=request.role_name,
            )
        )

        db.commit()

        return CreateStaffResponse(
            user=_build_admin_user_response(user),
            invitation_token=invitation_token,
            invitation_expires_at=expires_at,
        )

    except RoleNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except RoleAlreadyAssignedError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except UserAlreadyExistsError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Get hospital user",
)
def get_user(
    user_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Retrieve a user belonging to the authenticated Hospital.

    Cross-hospital user access is prevented by the repository
    hospital scope.
    """

    repository = _get_identity_repository(db)

    user = repository.get_user_by_id_in_hospital(
        hospital_id=context.hospital_id,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return _build_admin_user_response(
        user,
    )


# ============================================================================
# Roles
# ============================================================================


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="List hospital roles",
)
def list_roles(
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Return all roles belonging to the authenticated Hospital.
    """

    service = RoleService(
        repository=_get_identity_repository(db),
    )

    roles = service.list_roles(
        context=context,
    )

    return [
        RoleResponse.model_validate(role)
        for role in roles
    ]


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Get hospital role",
)
def get_role(
    role_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Retrieve a role belonging to the authenticated Hospital.
    """

    service = RoleService(
        repository=_get_identity_repository(db),
    )

    try:
        role = service.get_role(
            context=context,
            role_id=role_id,
        )

        return RoleResponse.model_validate(
            role,
        )

    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create hospital role",
)
def create_role(
    request: CreateRoleRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Create a new role belonging to the authenticated Hospital.
    """

    service = RoleService(
        repository=_get_identity_repository(db),
    )

    try:
        role = service.create_role(
            context=context,
            name=request.name,
            description=request.description,
        )

        return RoleResponse.model_validate(
            role,
        )

    except RoleAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Update hospital role",
)
def update_role(
    role_id: UUID,
    request: UpdateRoleRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Update a role belonging to the authenticated Hospital.
    """

    service = RoleService(
        repository=_get_identity_repository(db),
    )

    try:
        role = service.update_role(
            context=context,
            role_id=role_id,
            name=request.name,
            description=request.description,
        )

        return RoleResponse.model_validate(
            role,
        )

    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except RoleAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete hospital role",
)
def delete_role(
    role_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Delete a role belonging to the authenticated Hospital.

    Associated RolePermission and UserRole records are removed
    through the configured model relationships.
    """

    service = RoleService(
        repository=_get_identity_repository(db),
    )

    try:
        service.delete_role(
            context=context,
            role_id=role_id,
        )

    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================================
# Role Permissions
# ============================================================================


@router.post(
    "/roles/{role_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign permission to role",
)
def assign_permission(
    role_id: UUID,
    request: AssignPermissionRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Assign a platform permission to a hospital role.

    The role is first resolved using the authenticated hospital
    context so that an administrator cannot modify a role belonging
    to another hospital.
    """

    repository = _get_identity_repository(db)

    _get_hospital_role_or_404(
        repository=repository,
        context=context,
        role_id=role_id,
    )

    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    try:
        service.assign_permission(
            role_id=role_id,
            permission_code=request.permission_code,
        )

        db.commit()

    except PermissionNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/roles/{role_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="List role permissions",
)
def list_permissions(
    role_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Return all permissions assigned to a hospital role.

    The role must belong to the authenticated Hospital.
    """

    repository = _get_identity_repository(db)

    _get_hospital_role_or_404(
        repository=repository,
        context=context,
        role_id=role_id,
    )

    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    permissions = service.list_permissions(
        role_id=role_id,
    )

    return RolePermissionsResponse(
        permissions=[
            PermissionResponse.model_validate(
                permission,
            )
            for permission in permissions
        ],
    )


@router.delete(
    "/roles/{role_id}/permissions/{permission_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove permission from role",
)
def remove_permission(
    role_id: UUID,
    permission_code: str,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Remove a permission from a hospital role.

    The role must belong to the authenticated Hospital.
    """

    repository = _get_identity_repository(db)

    _get_hospital_role_or_404(
        repository=repository,
        context=context,
        role_id=role_id,
    )

    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    try:
        service.remove_permission(
            role_id=role_id,
            permission_code=permission_code,
        )

        db.commit()

    except PermissionNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================================
# User Roles
# ============================================================================


@router.post(
    "/users/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign role to user",
)
def assign_role_to_user(
    user_id: UUID,
    request: AssignRoleRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Assign a hospital role to an existing user.

    The target user must belong to the authenticated Hospital.

    The authenticated administrator is recorded as the user
    who performed the assignment.
    """

    repository = _get_identity_repository(db)

    user = repository.get_user_by_id_in_hospital(
        hospital_id=context.hospital_id,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    service = UserService(
        repository=repository,
    )

    try:
        service.assign_role(
            user=user,
            role_name=request.role_name,
            assigned_by_user_id=context.user_id,
        )

        db.commit()

    except RoleNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except RoleAlreadyAssignedError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/users/{user_id}/roles/{role_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove role from user",
)
def remove_role_from_user(
    user_id: UUID,
    role_name: str,
    context: RequestContext = Depends(
        get_request_context,
    ),
    db: Session = Depends(get_db),
    _=Depends(
        require_role("Administrator"),
    ),
):
    """
    Remove an active role assignment from a user.

    The UserRole record is retained and marked inactive so
    that assignment history is preserved.
    """

    repository = _get_identity_repository(db)

    user = repository.get_user_by_id_in_hospital(
        hospital_id=context.hospital_id,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    service = UserService(
        repository=repository,
    )

    try:
        service.remove_role(
            user=user,
            role_name=role_name,
        )

        db.commit()

    except RoleNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except UserRoleNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc