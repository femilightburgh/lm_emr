"""
========================================================================

LIGHTBURGH EMR

User Service

========================================================================
"""

from uuid import UUID

from app.core.security.hashing import hash_password
from app.modules.identity.enums import AccountStatus
from app.modules.identity.exceptions import (
    HospitalNotFoundError,
    RoleNotFoundError,
    UserAlreadyExistsError,
)
from app.modules.identity.models import UserAccount, UserRole
from app.modules.identity.repository import IdentityRepository


class UserService:
    """
    Business logic for user lifecycle management.

    Responsibilities
    ----------------
    - Create user accounts
    - Assign roles to users

    This service DOES NOT:
    - Commit transactions
    - Authenticate users
    - Generate JWT tokens
    """

    def __init__(self, repository: IdentityRepository):
        self.repository = repository

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

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
            hospital_code
        )

        if hospital is None:
            raise HospitalNotFoundError(
                "Hospital not found."
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
                "A user with this email already exists."
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

        NOTE:
        This method DOES NOT commit.
        """

        user = UserAccount(
            hospital_id=hospital_id,
            email=email.lower(),
            password_hash=hash_password(password),
            status=AccountStatus.ACTIVE,
            is_superuser=False,
        )

        self.repository.create_user(user)

        # Generate the UUID before assigning roles.
        self.repository.flush()

        return user

    # ------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------

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

        NOTE:
        This method DOES NOT commit the transaction.
        """

        hospital = self._get_hospital_or_raise(
            hospital_code
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

    def assign_role(
        self,
        *,
        user: UserAccount,
        role_name: str,
        assigned_by_user_id: UUID | None = None,
    ) -> UserRole:
        """
        Assign a role to an existing user.

        NOTE:
        This method DOES NOT commit.
        """

        role = self.repository.get_role_by_name(
            hospital_id=user.hospital_id,
            role_name=role_name,
        )

        if role is None:
            raise RoleNotFoundError(
                f"Role '{role_name}' does not exist."
            )

        user_role = UserRole(
            user_account_id=user.id,
            role_id=role.id,
            assigned_by_user_id=assigned_by_user_id,
            is_active=True,
        )

        self.repository.create_user_role(user_role)

        return user_role