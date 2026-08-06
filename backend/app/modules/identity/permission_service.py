"""
========================================================================

LIGHTBURGH EMR

Permission Service

========================================================================

Purpose
-------

Business logic for platform permissions.

Responsibilities
----------------
- Synchronize registered permissions
- Retrieve permissions
- Validate permission codes

========================================================================
"""

from app.modules.identity.models import Permission
from app.modules.identity.permission_definition import PermissionDefinition
from app.modules.identity.permission_repository import PermissionRepository
from app.modules.identity.registry import permission_registry


class PermissionService:
    """
    Business logic for platform permissions.
    """

    def __init__(
        self,
        repository: PermissionRepository,
    ) -> None:
        self.repository = repository

    def sync_permissions(self) -> None:
        """
        Synchronize the registered permission catalogue with
        the database.

        Safe to execute repeatedly.
        """

        registered = self._registered_permissions()
        existing = self._existing_permissions()

        self._create_missing_permissions(
            registered=registered,
            existing=existing,
        )

        self._update_existing_permissions(
            registered=registered,
            existing=existing,
        )

    def _registered_permissions(
        self,
    ) -> dict[str, PermissionDefinition]:
        """
        Return registered permissions indexed by code.
        """

        return {
            permission.code: permission
            for permission in permission_registry.get_all()
        }

    def _existing_permissions(
        self,
    ) -> dict[str, Permission]:
        """
        Return database permissions indexed by code.
        """

        return {
            permission.code: permission
            for permission in self.repository.get_all()
        }

    def _create_missing_permissions(
        self,
        *,
        registered: dict[str, PermissionDefinition],
        existing: dict[str, Permission],
    ) -> None:
        """
        Create permissions that do not yet exist.
        """

        for code, definition in registered.items():

            if code in existing:
                continue

            self.repository.create_from_definition(
                definition,
            )

    def _update_existing_permissions(
        self,
        *,
        registered: dict[str, PermissionDefinition],
        existing: dict[str, Permission],
    ) -> None:
        """
        Synchronize mutable permission attributes.
        """

        for code, permission in existing.items():

            definition = registered.get(code)

            if definition is None:
                continue

            permission.name = definition.name
            permission.description = definition.description
            permission.is_platform_permission = True