"""
========================================================================

LIGHTBURGH EMR

Authentication Service

========================================================================

Responsible for authenticating users and issuing JWT tokens.

Responsibilities
----------------
- Validate hospital
- Authenticate user credentials
- Verify account status
- Load user roles
- Generate JWT access and refresh tokens

This service contains no SQLAlchemy queries. All database access must
be delegated to IdentityRepository.

========================================================================
"""

from app.core.security.hashing import verify_password
from app.modules.identity.models import AccountStatus
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.token_service import TokenService
from app.modules.identity.schemas import LoginResponse
from app.modules.identity.exceptions import (
    InvalidCredentialsError,
    InactiveAccountError,
    InvalidTokenError,
    ExpiredTokenError,
)
from uuid import UUID


class AuthService:
    """
    Service responsible for authenticating users.
    """

    def __init__(
        self,
        repository: IdentityRepository,
        token_service: TokenService,
    ) -> None:
        self.repository = repository
        self.token_service = token_service

    def login(
        self,
        *,
        hospital_code: str,
        email: str,
        password: str,
    ) -> LoginResponse:
        """
        Authenticate a user and issue JWT tokens.

        Workflow
        --------
        1. Validate hospital.
        2. Retrieve user.
        3. Verify password.
        4. Verify account status.
        5. Retrieve user roles.
        6. Generate access token.
        7. Generate refresh token.

        Returns
        -------
        dict
            Authentication response containing JWT tokens.
        """

        hospital = self._get_hospital_or_raise(hospital_code)

        user = self._get_user_or_raise(
            hospital_id=hospital.id,
            email=email,
        )

        self._verify_password(
            password=password,
            password_hash=user.password_hash,
        )

        self._validate_account_status(user.status)

        roles = self._get_user_role_names(user.id)

        access_token = self.token_service.create_access_token(
            user_id=user.id,
            hospital_id=hospital.id,
            roles=roles,
        )

        refresh_token = self.token_service.create_refresh_token(
            user_id=user.id,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


    def refresh(
        self,
        *,
        refresh_token: str,
    ) -> LoginResponse:
        """
        Validate a refresh token and issue a new access token.

        The refresh token itself is not rotated yet.

        Workflow
        --------
        1. Decode the refresh token.
        2. Verify that it is a refresh token.
        3. Retrieve the user.
        4. Verify that the account is active.
        5. Retrieve the user's current roles.
        6. Issue a new access token.
        """

        payload = self.token_service.decode_token(
            refresh_token,
        )

        if payload.get(
            self.token_service.CLAIM_TOKEN_TYPE,
        ) != self.token_service.REFRESH_TOKEN:
            raise InvalidTokenError()

        user_id = payload.get(
            self.token_service.CLAIM_SUBJECT,
        )

        if not user_id:
            raise InvalidTokenError()

        user = self.repository.get_user_by_id(
            UUID(user_id),
        )

        if user is None:
            raise InvalidTokenError()

        self._validate_account_status(
            user.status,
        )

        roles = self._get_user_role_names(
            user.id,
        )

        access_token = self.token_service.create_access_token(
            user_id=user.id,
            hospital_id=user.hospital_id,
            roles=roles,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


    def _get_hospital_or_raise(
        self,
        hospital_code: str,
    ):
        """
        Retrieve a hospital by code.

        Raises
        ------
        Appropriate application exception if the hospital does not exist.
        """

        hospital = self.repository.get_hospital_by_code(
            hospital_code,
        )

        if hospital is None:
            raise InvalidCredentialsError()

        return hospital

    def _get_user_or_raise(
        self,
        hospital_id: UUID,
        email: str,
    ):
        """
        Retrieve a user by hospital and email.

        Raises
        ------
        Appropriate application exception if the user does not exist.
        """

        user = self.repository.get_user_by_email(
            hospital_id=hospital_id,
            email=email,
        )

        if user is None:
            raise InvalidCredentialsError()

        return user

    def _verify_password(
        self,
        *,
        password: str,
        password_hash: str,
    ) -> None:

        if not verify_password(password, password_hash):
            raise InvalidCredentialsError()

    def _validate_account_status(
        self,
        status: AccountStatus,
    ) -> None:
        """
        Ensure the account is active.

        Raises
        ------
        Appropriate application exception if the account is not active.
        """

        if status != AccountStatus.ACTIVE:
            raise InactiveAccountError()

    def _get_user_role_names(
        self,
        user_id: UUID,
    ) -> list[str]:
        """
        Retrieve the names of all roles assigned to a user.
        """

        return self.repository.get_user_role_names(user_id)