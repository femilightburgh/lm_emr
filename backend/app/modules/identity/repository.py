"""
========================================================================

LIGHTBURGH EMR

Identity Repository

========================================================================

Repository Responsibilities
---------------------------

The repository layer is responsible ONLY for database access.

It should never contain business rules.

Responsibilities include:

• Retrieving users
• Creating users
• Retrieving hospitals
• Retrieving roles
• Assigning roles
• Loading permissions

Business decisions belong inside the service layer.

========================================================================
"""

from uuid import UUID
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import (
    Permission,
    Role,
    RolePermission,
    UserAccount,
    UserRole,
)
from app.modules.organization.models import Hospital


class IdentityRepository:
    """
    Repository responsible for database access for the
    Identity module.

    This repository intentionally contains NO business logic.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # Hospital
    # ==========================================================

    def get_hospital_by_code(
        self,
        hospital_code: str,
    ) -> Hospital | None:
        """
        Retrieve a hospital using its unique hospital code.
        """

        statement = (
            select(Hospital)
            .where(Hospital.code == hospital_code)
        )

        return self.db.scalar(statement)

    # ==========================================================
    # Users
    # ==========================================================

    def get_user_by_email(
        self,
        hospital_id: UUID,
        email: str,
    ) -> UserAccount | None:
        """
        Retrieve a user using hospital and email.

        Emails are unique only within a hospital.
        """

        statement = (
            select(UserAccount)
            .where(
                UserAccount.hospital_id == hospital_id,
                UserAccount.email == email,
            )
        )

        return self.db.scalar(statement)
    

    def create_user(
        self,
        user: UserAccount,
    ) -> UserAccount:
        """
        Add a user to the current session.

        Does NOT commit.
        """

        self.db.add(user)
        return user
    
    def get_user_by_id(
        self,
        user_id: UUID,
    ) -> UserAccount | None:
        """
        Retrieve a user by ID.
        """

        statement = (
            select(UserAccount)
            .where(UserAccount.id == user_id)
        )

        return self.db.scalar(statement)

    # ==========================================================
    # Roles
    # ==========================================================

    def get_role_by_name(
        self,
        hospital_id: UUID,
        role_name: str,
    ) -> Role | None:
        """
        Retrieve a role by hospital and name.
        """

        statement = (
            select(Role)
            .where(
                Role.hospital_id == hospital_id,
                Role.name == role_name,
            )
        )

        return self.db.scalar(statement)

    def create_user_role(
        self,
        user_role: UserRole,
    ) -> UserRole:
        """
        Add a user-role assignment to the current session.

        Does NOT commit.
        """

        self.db.add(user_role)
        return user_role
    
    def get_user_role_names(
        self,
        user_id: UUID,
    ) -> list[str]:
        """
        Retrieve all role names assigned to a user.
        """

        statement = (
            select(Role.name)
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(UserRole.user_account_id == user_id)
        )

        return list(self.db.scalars(statement).all())
    
    def user_has_role(
        self,
        *,
        user_id: UUID,
        role_name: str,
    ) -> bool:
        """
        Determine whether a user possesses an active role.
        """

        statement = (
            select(UserRole.id)
            .join(
                Role,
                Role.id == UserRole.role_id,
            )
            .where(
                UserRole.user_account_id == user_id,
                UserRole.is_active.is_(True),
                Role.name == role_name,
            )
        )

        return self.db.scalar(statement) is not None
    
    def get_user_permission_codes(
        self,
        user_id: UUID,
    ) -> list[str]:
        """
        Retrieve all permission codes assigned to a user.

        Permissions are inherited through the user's roles.
        """

        statement = (
            select(Permission.code)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(
                Role,
                Role.id == RolePermission.role_id,
            )
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_account_id == user_id,
                UserRole.is_active.is_(True),
            )
            .distinct()
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ==========================================================
    # Transaction helpers
    # ==========================================================

    def flush(self) -> None:
        """
        Flush pending changes without committing.

        Useful when IDs are required before commit.
        """

        self.db.flush()

    def save(self) -> None:
        """
        Commit the current transaction.
        """

        self.db.commit()

    def refresh(
        self,
        entity: Any,
    ) -> None:
        """
        Refresh an entity from the database.
        """

        self.db.refresh(entity)

    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """

        self.db.rollback()