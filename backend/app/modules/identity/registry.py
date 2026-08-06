"""
========================================================================

LIGHTBURGH EMR

Permission Registry Engine

========================================================================

Purpose
-------

Provides a central registry for platform permissions.

Modules register their permission definitions here.

The registry serves as the canonical source of truth for every
permission supported by the platform.

========================================================================
"""

from app.modules.identity.permission_definition import (
    PermissionDefinition,
)


class PermissionRegistry:
    """
    Registry of all platform permissions.
    """

    def __init__(self) -> None:
        self._permissions: dict[str, PermissionDefinition] = {}

    def register(
        self,
        permissions: list[PermissionDefinition],
    ) -> None:
        """
        Register one or more permission definitions.
        """

        for permission in permissions:

            if permission.code in self._permissions:
                raise ValueError(
                    f"Duplicate permission: {permission.code}"
                )

            self._permissions[permission.code] = permission

    def get_all(
        self,
    ) -> list[PermissionDefinition]:
        """
        Return all registered permissions.
        """

        return list(self._permissions.values())

    def find_by_code(
        self,
        code: str,
    ) -> PermissionDefinition | None:
        """
        Retrieve a permission by its code.
        """

        return self._permissions.get(code)


permission_registry = PermissionRegistry()