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

        Registration is idempotent. Re-registering an
        already-known permission is allowed as long as the
        definition is the same.
        """

        for permission in permissions:
            existing = self._permissions.get(
                permission.code,
            )

            if existing is not None:
                if existing != permission:
                    raise ValueError(
                        f"Conflicting permission definition: "
                        f"{permission.code}"
                    )

                continue

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