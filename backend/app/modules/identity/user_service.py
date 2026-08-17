"""
========================================================================

LIGHTBURGH EMR

User Service

========================================================================

Business logic for user lifecycle and role assignment.

Database access belongs in IdentityRepository.

Authentication belongs in AuthService.

HTTP concerns belong in routers.

========================================================================
"""

from uuid import UUID

from app.core.context import RequestContext
from app.core.security.hashing import hash_password
from app.modules.identity.enums import AccountStatus
from app.modules.identity.exceptions import (
    HospitalNotFoundError,
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    UserAlreadyExistsError,
    UserRoleNotFoundError,
)
from app.modules.identity.models import (
    UserAccount,
    UserRole,
)
from app.modules.identity.repository import IdentityRepository


class UserService:
    """
    Business logic for user lifecycle management.

    Responsibilities
    ----------------
    - List hospital users
    - Create user accounts
    - Assign initial roles
    - Assign roles to existing users
    - Reactivate inactive role assignments
    - Deactivate role assignments

    This service DOES NOT:
    - Commit transactions
    - Authenticate users
    - Generate JWT tokens
    """

    def __init__(
        self,
        repository: IdentityRepository,
    ) -> None:
        self.repository = repository

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _get_hospital_or_raise(
        self,
        hospital_code: str,
    ):
        """
        Retrieve a hospital by code.

        Raises:
            HospitalNotFoundError
                If the hospital does not exist.
        """

        hospital = self.repository.get_hospital_by_code(
            hospital_code,
        )

        if hospital is None:
            raise HospitalNotFoundError(
                "Hospital not found.",
            )

        return hospital

    def _ensure_email_is_available(
        self,
        *,
        hospital_id: UUID,
        email: str,
    ) -> None:
        """
        Ensure that no user already exists with the
        supplied email within the hospital.
        """

        existing_user = self.repository.get_user_by_email(
            hospital_id=hospital_id,
            email=email,
        )

        if existing_user is not None:
            raise UserAlreadyExistsError(
                "A user with this email already exists.",
            )

    def _create_user_account(
        self,
        *,
        hospital_id: UUID,
        email: str,
        password: str,
    ) -> UserAccount:
        """
        Create a new user account.

        This method does NOT commit.
        """

        user = UserAccount(
            hospital_id=hospital_id,
            email=email.lower(),
            password_hash=hash_password(password),
            status=AccountStatus.ACTIVE,
            is_superuser=False,
        )

        self.repository.create_user(
            user,
        )

        # Generate the UUID before assigning roles.
        self.repository.flush()

        return user

    def _get_role_or_raise(
        self,
        *,
        hospital_id: UUID,
        role_name: str,
    ):
        """
        Retrieve a role belonging to the supplied hospital.

        Raises:
            RoleNotFoundError
                If the role does not exist.
        """

        normalized_role_name = role_name.strip()

        role = self.repository.get_role_by_name(
            hospital_id=hospital_id,
            role_name=normalized_role_name,
        )

        if role is None:
            raise RoleNotFoundError(
                f"Role '{normalized_role_name}' does not exist.",
            )

        return role

    # =========================================================================
    # List Users
    # =========================================================================

    def list_users(
        self,
        *,
        context: RequestContext,
    ) -> list[UserAccount]:
        """
        Return all users belonging to the authenticated Hospital.

        Hospital tenancy is enforced through the RequestContext.
        """

        return self.repository.list_users(
            hospital_id=context.hospital_id,
        )

    # =========================================================================
    # User Creation
    # =========================================================================

    def create_user(
        self,
        *,
        hospital_code: str,
        email: str,
        password: str,
        role_name: str,
    ) -> UserAccount:
        """
        Create a new user and assign an initial role.

        This method does NOT commit the transaction.
        """

        hospital = self._get_hospital_or_raise(
            hospital_code,
        )

        self._ensure_email_is_available(
            hospital_id=hospital.id,
            email=email,
        )

        user = self._create_user_account(
            hospital_id=hospital.id,
            email=email,
            password=password,
        )

        self.assign_role(
            user=user,
            role_name=role_name,
        )

        return user

    # =========================================================================
    # Assign Role
    # =========================================================================

    def assign_role(
        self,
        *,
        user: UserAccount,
        role_name: str,
        assigned_by_user_id: UUID | None = None,
    ) -> UserRole:
        """
        Assign a role to an existing user.

        Assignment behavior:

        1. Role does not exist:
           RoleNotFoundError

        2. Active assignment already exists:
           RoleAlreadyAssignedError

        3. Inactive assignment exists:
           Reactivate the existing assignment.

        4. No assignment exists:
           Create a new UserRole.

        This method does NOT commit.
        """

        role = self._get_role_or_raise(
            hospital_id=user.hospital_id,
            role_name=role_name,
        )

        existing_assignment = self.repository.get_user_role(
            user_id=user.id,
            role_id=role.id,
        )

        # ------------------------------------------------------------------
        # Existing Assignment
        # ------------------------------------------------------------------

        if existing_assignment is not None:

            if existing_assignment.is_active:
                raise RoleAlreadyAssignedError(
                    f"Role '{role.name}' is already assigned "
                    "to this user.",
                )

            # --------------------------------------------------------------
            # Reactivate Historical Assignment
            # --------------------------------------------------------------

            existing_assignment.is_active = True
            existing_assignment.assigned_by_user_id = (
                assigned_by_user_id
            )
            existing_assignment.expires_at = None

            return existing_assignment

        # ------------------------------------------------------------------
        # New Assignment
        # ------------------------------------------------------------------

        user_role = UserRole(
            user_account_id=user.id,
            role_id=role.id,
            assigned_by_user_id=assigned_by_user_id,
            is_active=True,
        )

        self.repository.create_user_role(
            user_role,
        )

        return user_role

    # =========================================================================
    # Remove Role
    # =========================================================================

    def remove_role(
        self,
        *,
        user: UserAccount,
        role_name: str,
    ) -> UserRole:
        """
        Deactivate an active role assignment.

        Role assignments are intentionally not deleted.

        This preserves the UserRole record for future audit,
        historical reporting, and lifecycle management.

        This method does NOT commit.
        """

        role = self._get_role_or_raise(
            hospital_id=user.hospital_id,
            role_name=role_name,
        )

        user_role = self.repository.get_user_role(
            user_id=user.id,
            role_id=role.id,
        )

        if (
            user_role is None
            or not user_role.is_active
        ):
            raise UserRoleNotFoundError(
                f"Role '{role.name}' is not currently "
                "assigned to this user.",
            )

        self.repository.deactivate_user_role(
            user_role,
        )

        return user_role