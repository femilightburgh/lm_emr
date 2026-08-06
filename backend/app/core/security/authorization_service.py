"""
========================================================================

LIGHTBURGH EMR

Authorization Service

========================================================================

Purpose
-------

Business service responsible for runtime authorization decisions.

Responsibilities
----------------
- Determine whether a user possesses a role
- Determine whether a user possesses a permission

Contains business logic only.

========================================================================
"""

from uuid import UUID

from app.core.security.authorization_repository import (
    AuthorizationRepository,
)


class AuthorizationService:
    """
    Service responsible for runtime authorization.
    """

    def __init__(
        self,
        repository: AuthorizationRepository,
    ) -> None:
        self.repository = repository

    def has_role(
        self,
        *,
        user_id: UUID,
        role_name: str,
    ) -> bool:
        """
        Determine whether a user possesses a role.
        """

        return self.repository.role_exists_for_user(
            user_id=user_id,
            role_name=role_name,
        )

    def has_permission(
        self,
        *,
        user_id: UUID,
        permission_code: str,
    ) -> bool:
        """
        Determine whether a user possesses a permission.
        """

        return self.repository.permission_exists_for_user(
            user_id=user_id,
            permission_code=permission_code,
        )