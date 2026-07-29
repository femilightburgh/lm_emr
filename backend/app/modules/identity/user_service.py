"""
========================================================================

LIGHTBURGH EMR

User Service

========================================================================
"""

from uuid import UUID

from app.core.security.hashing import hash_password
from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount, UserRole
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.exceptions import (
    HospitalNotFoundError,
    RoleNotFoundError,
    UserAlreadyExistsError,
)


class UserService:
    """
    Business logic for user lifecycle management.

    This service is responsible for:

    - Creating users
    - Assigning roles

    It DOES NOT:
    - Authenticate users
    - Generate JWTs
    - Commit transactions
    """

    def __init__(self, repository: IdentityRepository):
        self.repository = repository

    def create_user(
        self,
        *,
        hospital_code: str,
        email: str,
        password: str,
        role_name: str,
    ) -> UserAccount:
        """
        Create a user account.

        NOTE:
        This method DOES NOT commit the transaction.
        """

        hospital = self.repository.get_hospital_by_code(hospital_code)

        if hospital is None:
            raise HospitalNotFoundError(
                "Hospital not found."
            )

        existing_user = self.repository.get_user_by_email(
            hospital_id=hospital.id,
            email=email,
        )

        if existing_user is not None:
            raise UserAlreadyExistsError(
                "A user with this email already exists."
            )

        user = UserAccount(
            hospital_id=hospital.id,
            email=email.lower(),
            password_hash=hash_password(password),
            status=AccountStatus.PENDING,
            is_superuser=False,
        )

        self.repository.create_user(user)

        # Generate the UUID before role assignment
        self.repository.flush()

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