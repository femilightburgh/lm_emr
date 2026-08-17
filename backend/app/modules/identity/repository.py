"""
========================================================================

LIGHTBURGH EMR

Identity Repository

========================================================================

Database access for Identity entities.

Business logic belongs in services.

HTTP concerns belong in routers.

========================================================================
"""

from uuid import UUID

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
    Repository for Identity-related database operations.

    The repository does not commit transactions unless explicitly
    instructed by the caller.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # =========================================================================
    # Hospital
    # =========================================================================

    def get_hospital_by_code(
        self,
        hospital_code: str,
    ) -> Hospital | None:
        """
        Retrieve a Hospital by its unique code.
        """

        statement = (
            select(Hospital)
            .where(
                Hospital.code == hospital_code,
            )
        )

        return self.db.scalar(statement)

    # =========================================================================
    # Users
    # =========================================================================

    def get_user_by_email(
        self,
        *,
        hospital_id: UUID,
        email: str,
    ) -> UserAccount | None:
        """
        Retrieve a user by email within a specific Hospital.
        """

        statement = (
            select(UserAccount)
            .where(
                UserAccount.hospital_id == hospital_id,
                UserAccount.email == email.lower(),
            )
        )

        return self.db.scalar(statement)

    def create_user(
        self,
        user: UserAccount,
    ) -> UserAccount:
        """
        Add a UserAccount to the current session.

        Does NOT commit.
        """

        self.db.add(user)

        return user

    def get_user_by_id(
        self,
        user_id: UUID,
    ) -> UserAccount | None:
        """
        Retrieve a UserAccount by ID.

        This method is intended for internal identity lookups,
        such as authentication and token refresh.
        """

        statement = (
            select(UserAccount)
            .where(
                UserAccount.id == user_id,
            )
        )

        return self.db.scalar(statement)

    def get_user_by_id_in_hospital(
        self,
        *,
        hospital_id: UUID,
        user_id: UUID,
    ) -> UserAccount | None:
        """
        Retrieve a UserAccount by ID while enforcing
        hospital tenancy.
        """

        statement = (
            select(UserAccount)
            .where(
                UserAccount.id == user_id,
                UserAccount.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    def list_users(
        self,
        *,
        hospital_id: UUID,
    ) -> list[UserAccount]:
        """
        Retrieve all user accounts belonging to a Hospital.

        Results are ordered by email for stable administrative
        presentation.
        """

        statement = (
            select(UserAccount)
            .where(
                UserAccount.hospital_id == hospital_id,
            )
            .order_by(
                UserAccount.email.asc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    # =========================================================================
    # Roles
    # =========================================================================

    def get_role_by_name(
        self,
        *,
        hospital_id: UUID,
        role_name: str,
    ) -> Role | None:
        """
        Retrieve a role belonging to a Hospital by name.
        """

        statement = (
            select(Role)
            .where(
                Role.hospital_id == hospital_id,
                Role.name == role_name,
            )
        )

        return self.db.scalar(statement)

    def list_roles(
        self,
        *,
        hospital_id: UUID,
    ) -> list[Role]:
        """
        Retrieve all roles belonging to a Hospital.
        """

        statement = (
            select(Role)
            .where(
                Role.hospital_id == hospital_id,
            )
            .order_by(
                Role.name.asc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_role_by_id(
        self,
        *,
        hospital_id: UUID,
        role_id: UUID,
    ) -> Role | None:
        """
        Retrieve a role belonging to a Hospital.
        """

        statement = (
            select(Role)
            .where(
                Role.id == role_id,
                Role.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    def create_role(
        self,
        role: Role,
    ) -> Role:
        """
        Add a Role to the current session.

        Does NOT commit.
        """

        self.db.add(role)

        return role

    def delete_role(
        self,
        role: Role,
    ) -> None:
        """
        Delete a Role from the current session.

        Does NOT commit.
        """

        self.db.delete(role)

    # =========================================================================
    # User Roles
    # =========================================================================

    def create_user_role(
        self,
        user_role: UserRole,
    ) -> UserRole:
        """
        Add a UserRole assignment to the current session.

        Does NOT commit.
        """

        self.db.add(user_role)

        return user_role

    def get_user_role(
        self,
        *,
        user_id: UUID,
        role_id: UUID,
    ) -> UserRole | None:
        """
        Retrieve a specific UserRole assignment.

        Both active and inactive assignments are returned.

        This allows an inactive historical assignment to be
        reactivated instead of creating a duplicate row.
        """

        statement = (
            select(UserRole)
            .where(
                UserRole.user_account_id == user_id,
                UserRole.role_id == role_id,
            )
        )

        return self.db.scalar(statement)

    def list_user_roles(
        self,
        *,
        user_id: UUID,
    ) -> list[UserRole]:
        """
        Retrieve all role assignments belonging to a user.
        """

        statement = (
            select(UserRole)
            .where(
                UserRole.user_account_id == user_id,
            )
            .order_by(
                UserRole.assigned_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def deactivate_user_role(
        self,
        user_role: UserRole,
    ) -> None:
        """
        Deactivate a UserRole assignment.

        The assignment is retained for historical and audit
        purposes.

        Does NOT commit.
        """

        user_role.is_active = False

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
            .where(
                UserRole.user_account_id == user_id,
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

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

    # =========================================================================
    # Permissions
    # =========================================================================

    def get_user_permission_codes(
        self,
        user_id: UUID,
    ) -> list[str]:
        """
        Retrieve all permission codes assigned to a user.

        Permissions are inherited through the user's active roles.
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

    # =========================================================================
    # Transaction Helpers
    # =========================================================================

    def flush(
        self,
    ) -> None:
        """
        Flush pending changes without committing.

        Useful when IDs are required before subsequent operations.
        """

        self.db.flush()

    def save(
        self,
    ) -> None:
        """
        Commit the current transaction.
        """

        self.db.commit()

    def refresh(
        self,
        entity,
    ) -> None:
        """
        Refresh an entity from the database.
        """

        self.db.refresh(entity)

    def rollback(
        self,
    ) -> None:
        """
        Roll back the current transaction.
        """

        self.db.rollback()