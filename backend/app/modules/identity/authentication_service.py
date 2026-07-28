"""
========================================================================

LIGHTBURGH EMR

Authentication Service

========================================================================

Responsibilities
----------------

The Authentication Service coordinates the complete login workflow.

It is responsible for:

• Locating the hospital from its public hospital code
• Finding the user within that hospital
• Verifying the supplied password
• Validating account status
• Resetting or incrementing failed login attempts
• Recording successful login timestamps
• Generating JWT access and refresh tokens

Business rules belong here.

Database queries belong in repositories.

========================================================================
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.common.exceptions import InvalidCredentialsException
from app.core.config import settings
from app.core.security.hashing import verify_password
from app.core.security.tokens import (
    create_access_token,
    create_refresh_token,
)
from app.modules.identity.enums import AccountStatus
from app.modules.identity.repository import IdentityRepository
from app.modules.organization.repository import OrganizationRepository


class AuthenticationService:
    """
    Coordinates user authentication for the LIGHTBURGH platform.
    """

    MAX_FAILED_ATTEMPTS = settings.max_failed_login_attempts

    def __init__(self, db: Session):
        self.db = db
        self.identity_repository = IdentityRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def authenticate(
        self,
        hospital_code: str,
        email: str,
        password: str,
    ):
        """
        Authenticate a user using:

        • Hospital Code
        • Email
        • Password

        Returns
        -------
        dict
            JWT access and refresh tokens.
        """

        # --------------------------------------------------------------
        # Step 1:
        # Resolve hospital from public hospital code.
        # --------------------------------------------------------------

        hospital = self.organization_repository.get_hospital_by_code(
            hospital_code
        )

        if hospital is None:
            raise InvalidCredentialsException()

        # --------------------------------------------------------------
        # Step 2:
        # Retrieve the user belonging to that hospital.
        # --------------------------------------------------------------

        user = self.identity_repository.get_user_by_email(
            hospital.id,
            email,
        )

        if user is None:
            raise InvalidCredentialsException()

        # --------------------------------------------------------------
        # Step 3:
        # Prevent login for inactive accounts.
        # --------------------------------------------------------------

        if user.status != AccountStatus.ACTIVE:
            raise InvalidCredentialsException()

        # --------------------------------------------------------------
        # Step 4:
        # Verify password.
        # --------------------------------------------------------------

        if not verify_password(password, user.password_hash):

            user.failed_login_attempts += 1

            if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
                user.status = AccountStatus.LOCKED

            self.identity_repository.save()

            raise InvalidCredentialsException()

        # --------------------------------------------------------------
        # Step 5:
        # Successful login.
        # Reset security counters.
        # --------------------------------------------------------------

        user.failed_login_attempts = 0
        user.last_login_at = datetime.now(UTC)

        self.identity_repository.save()
        self.identity_repository.refresh(user)

        # --------------------------------------------------------------
        # Step 6:
        # Generate JWT tokens.
        # --------------------------------------------------------------

        access_token = create_access_token(
            user_id=user.id,
            hospital_id=user.hospital_id,
        )

        refresh_token = create_refresh_token(
            user_id=user.id,
            hospital_id=user.hospital_id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }