"""
========================================================================

LIGHTBURGH EMR

Authorization Repository

========================================================================

Purpose
-------

Read-only repository for runtime authorization checks.

Responsibilities
----------------
- Determine whether a role exists for a user
- Determine whether a permission exists for a user

Contains no business logic.

========================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, exists, or_, select
from sqlalchemy.orm import Session

from app.modules.identity.models import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)


class AuthorizationRepository:
    """
    Repository responsible for runtime authorization queries.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def role_exists_for_user(
        self,
        *,
        user_id: UUID,
        role_name: str,
    ) -> bool:
        """
        Determine whether a user possesses a role.
        """

        statement = select(
            exists().where(
                UserRole.user_account_id == user_id,
                UserRole.role_id == Role.id,
                Role.name == role_name,
                self._active_assignment_clause(),
            )
        )

        return bool(self.session.scalar(statement))

    def permission_exists_for_user(
        self,
        *,
        user_id: UUID,
        permission_code: str,
    ) -> bool:
        """
        Determine whether a user possesses a permission.
        """

        statement = select(
            exists().where(
                UserRole.user_account_id == user_id,
                UserRole.role_id == Role.id,
                RolePermission.role_id == Role.id,
                RolePermission.permission_id == Permission.id,
                Permission.code == permission_code,
                self._active_assignment_clause(),
            )
        )

        return bool(self.session.scalar(statement))

    def _active_assignment_clause(self):
        """
        SQL clause identifying active role assignments.
        """

        return and_(
            UserRole.is_active.is_(True),
            or_(
                UserRole.expires_at.is_(None),
                UserRole.expires_at > datetime.now(UTC),
            ),
        )