"""
========================================================================

LIGHTBURGH EMR

Role Permission Repository

========================================================================

Purpose
-------

Database access layer for role permission assignments.

Responsibilities
----------------
- Create role permission assignments
- Delete role permission assignments
- Retrieve permissions assigned to roles

Contains no business logic.

========================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import RolePermission


class RolePermissionRepository:
    """
    Repository responsible for RolePermission persistence.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get_by_role(
        self,
        role_id: UUID,
    ) -> list[RolePermission]:
        """
        Retrieve all permission assignments for a role.
        """

        return list(
            self.session.scalars(
                select(RolePermission).where(
                    RolePermission.role_id == role_id
                )
            )
        )

    def get_by_role_and_permission(
        self,
        *,
        role_id: UUID,
        permission_id: UUID,
    ) -> RolePermission | None:
        """
        Retrieve a specific role permission assignment.
        """

        return self.session.scalar(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )

    def create(
        self,
        *,
        role_id: UUID,
        permission_id: UUID,
    ) -> RolePermission:
        """
        Create a new role permission assignment.
        """

        assignment = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )

        self.session.add(assignment)

        return assignment

    def delete(
        self,
        assignment: RolePermission,
    ) -> None:
        """
        Delete a role permission assignment.
        """

        self.session.delete(assignment)