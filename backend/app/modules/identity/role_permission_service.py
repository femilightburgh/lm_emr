"""
========================================================================

LIGHTBURGH EMR

Role Permission Service

========================================================================

Purpose
-------

Business logic for managing permission assignments to roles.

Responsibilities
----------------
- Assign permissions to roles
- Remove permissions from roles
- List permissions assigned to a role
- Determine whether a role possesses a permission

========================================================================
"""

from uuid import UUID

from app.modules.identity.models import Permission
from app.modules.identity.permission_repository import (
    PermissionRepository,
)
from app.modules.identity.role_permission_repository import (
    RolePermissionRepository,
)


class RolePermissionService:
    """
    Business logic for managing role permission assignments.
    """

    def __init__(
        self,
        repository: RolePermissionRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        self.repository = repository
        self.permission_repository = permission_repository

    def assign_permission(
        self,
        *,
        role_id: UUID,
        permission_code: str,
    ) -> None:
        """
        Assign a platform permission to a role.

        Safe to execute repeatedly.
        """

        permission = self.permission_repository.require_by_code(
            permission_code,
        )

        assignment = self.repository.get_by_role_and_permission(
            role_id=role_id,
            permission_id=permission.id,
        )

        if assignment is not None:
            return

        self.repository.create(
            role_id=role_id,
            permission_id=permission.id,
        )

    def remove_permission(
        self,
        *,
        role_id: UUID,
        permission_code: str,
    ) -> None:
        """
        Remove a platform permission from a role.

        Safe to execute repeatedly.
        """

        permission = self.permission_repository.require_by_code(
            permission_code,
        )

        assignment = self.repository.get_by_role_and_permission(
            role_id=role_id,
            permission_id=permission.id,
        )

        if assignment is None:
            return

        self.repository.delete(
            assignment,
        )

    def list_permissions(
        self,
        *,
        role_id: UUID,
    ) -> list[Permission]:
        """
        Return all permissions assigned to a role.
        """

        assignments = self.repository.get_by_role(
            role_id=role_id,
        )

        return [
            assignment.permission
            for assignment in assignments
        ]

    def has_permission(
        self,
        *,
        role_id: UUID,
        permission_code: str,
    ) -> bool:
        """
        Determine whether a role possesses a platform permission.
        """

        permission = self.permission_repository.get_by_code(
            permission_code,
        )

        if permission is None:
            return False

        assignment = self.repository.get_by_role_and_permission(
            role_id=role_id,
            permission_id=permission.id,
        )

        return assignment is not None