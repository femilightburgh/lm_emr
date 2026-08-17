"""
==============================================================================
LIGHTBURGH EMR

Role Service

==============================================================================

Business logic for managing hospital roles.

Roles are hospital-scoped authorization entities.

Permissions remain managed by RolePermissionService.

HTTP concerns belong in routers.
Database access belongs in repositories.
==============================================================================
"""

from uuid import UUID

from app.core.context import RequestContext
from app.modules.identity.exceptions import (
    RoleAlreadyExistsError,
    RoleNotFoundError,
)
from app.modules.identity.models import Role
from app.modules.identity.repository import IdentityRepository


class RoleService:
    """
    Service responsible for hospital role management.
    """

    def __init__(
        self,
        *,
        repository: IdentityRepository,
    ) -> None:
        self.repository = repository

    # =========================================================================
    # List Roles
    # =========================================================================

    def list_roles(
        self,
        *,
        context: RequestContext,
    ) -> list[Role]:
        """
        Return all roles belonging to the authenticated Hospital.
        """

        return self.repository.list_roles(
            hospital_id=context.hospital_id,
        )

    # =========================================================================
    # Get Role
    # =========================================================================

    def get_role(
        self,
        *,
        context: RequestContext,
        role_id: UUID,
    ) -> Role:
        """
        Retrieve a role belonging to the authenticated Hospital.
        """

        role = self.repository.get_role_by_id(
            hospital_id=context.hospital_id,
            role_id=role_id,
        )

        if role is None:
            raise RoleNotFoundError(
                f"Role '{role_id}' not found.",
            )

        return role

    # =========================================================================
    # Create Role
    # =========================================================================

    def create_role(
        self,
        *,
        context: RequestContext,
        name: str,
        description: str | None = None,
    ) -> Role:
        """
        Create a role belonging to the authenticated Hospital.
        """

        normalized_name = name.strip()

        existing_role = self.repository.get_role_by_name(
            hospital_id=context.hospital_id,
            role_name=normalized_name,
        )

        if existing_role is not None:
            raise RoleAlreadyExistsError(
                f"Role '{normalized_name}' already exists.",
            )

        role = Role(
            hospital_id=context.hospital_id,
            name=normalized_name,
            description=description.strip()
            if description is not None
            else None,
            is_template=False,
        )

        self.repository.create_role(
            role,
        )

        self.repository.save()
        self.repository.refresh(role)

        return role

    # =========================================================================
    # Update Role
    # =========================================================================

    def update_role(
        self,
        *,
        context: RequestContext,
        role_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Role:
        """
        Update a hospital role.
        """

        role = self.get_role(
            context=context,
            role_id=role_id,
        )

        normalized_name = name.strip()

        existing_role = self.repository.get_role_by_name(
            hospital_id=context.hospital_id,
            role_name=normalized_name,
        )

        if (
            existing_role is not None
            and existing_role.id != role.id
        ):
            raise RoleAlreadyExistsError(
                f"Role '{normalized_name}' already exists.",
            )

        role.name = normalized_name

        role.description = (
            description.strip()
            if description is not None
            else None
        )

        self.repository.save()
        self.repository.refresh(role)

        return role

    # =========================================================================
    # Delete Role
    # =========================================================================

    def delete_role(
        self,
        *,
        context: RequestContext,
        role_id: UUID,
    ) -> None:
        """
        Delete a hospital role.

        RolePermission and UserRole records associated with the
        role are removed through the model's configured cascade.
        """

        role = self.get_role(
            context=context,
            role_id=role_id,
        )

        self.repository.delete_role(
            role,
        )

        self.repository.save()