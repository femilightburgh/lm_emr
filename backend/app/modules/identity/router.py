"""
========================================================================

LIGHTBURGH EMR

Identity API Router

========================================================================

This router exposes authentication and identity endpoints.

Authorization administration endpoints belong in
`authorization_router.py`.

Business logic belongs in services.

Database access belongs in repositories.

The router should remain as thin as possible.

========================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security.dependencies import get_current_user
from app.db.session import get_db

from app.modules.identity.auth_service import AuthService
from app.modules.identity.exceptions import (
    ExpiredTokenError,
    InactiveAccountError,
    InvalidCredentialsError,
    InvalidTokenError,
    ExpiredInvitationError,
    InvalidInvitationError,
    InvitationAlreadyUsedError,
)
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import (
    CreateUserRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    UserResponse,
    ActivateUserRequest,
)
from app.modules.identity.token_service import TokenService
from app.modules.identity.user_service import UserService
from app.modules.identity.invitation_service import (
    InvitationService,
)


# ============================================================================
# Router
# ============================================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================================
# User Creation
# ============================================================================


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new user account and assign an initial role.
    """

    repository = IdentityRepository(db)

    service = UserService(
        repository,
    )

    user = service.create_user(
        hospital_code=request.hospital_code,
        email=request.email,
        password=request.password,
        role_name=request.role_name,
    )

    repository.save()
    repository.refresh(user)

    return UserResponse.model_validate(
        user,
    )


@router.post(
    "/activate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Activate a user account",
)
def activate_user(
    request: ActivateUserRequest,
    db: Session = Depends(get_db),
):
    """
    Activate a pending user account using a valid invitation.
    """

    repository = IdentityRepository(db)

    service = InvitationService(
        repository=repository,
    )

    try:
        service.activate_user(
            token=request.token,
            password=request.password,
        )

        db.commit()

    except InvalidInvitationError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except ExpiredInvitationError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except InvitationAlreadyUsedError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

# ============================================================================
# Login
# ============================================================================


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate a user",
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return JWT access and refresh tokens.
    """

    repository = IdentityRepository(db)

    token_service = TokenService()

    service = AuthService(
        repository=repository,
        token_service=token_service,
    )

    try:
        return service.login(
            hospital_code=request.hospital_code,
            email=request.email,
            password=request.password,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except InactiveAccountError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


# ============================================================================
# Refresh Token
# ============================================================================


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh an access token",
)
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Issue a new access token using a valid refresh token.
    """

    repository = IdentityRepository(db)

    token_service = TokenService()

    service = AuthService(
        repository=repository,
        token_service=token_service,
    )

    try:
        return service.refresh(
            refresh_token=request.refresh_token,
        )

    except InactiveAccountError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except ExpiredTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


# ============================================================================
# OAuth2 / Swagger Token Endpoint
# ============================================================================


@router.post(
    "/token",
    response_model=LoginResponse,
    summary="OAuth2 access token",
)
def oauth2_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible token endpoint.

    OAuth2 provides only a `username` field.

    LIGHTBURGH expects:

        hospital_code|email

    Example:

        WTH001|admin@lightburgh.com
    """

    repository = IdentityRepository(db)

    token_service = TokenService()

    service = AuthService(
        repository=repository,
        token_service=token_service,
    )

    try:
        hospital_code, email = form_data.username.split(
            "|",
            maxsplit=1,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Username must be in the format "
                "'hospital_code|email'."
            ),
        ) from exc

    try:
        return service.login(
            hospital_code=hospital_code,
            email=email,
            password=form_data.password,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except InactiveAccountError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


# ============================================================================
# Current User
# ============================================================================


@router.get(
    "/me",
    summary="Current authenticated user",
)
def me(
    current_user=Depends(get_current_user),
):
    """
    Return the currently authenticated user's identity
    and active roles.
    """

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "hospital_id": str(current_user.hospital_id),
        "status": current_user.status,
        "roles": [
            user_role.role.name
            for user_role in current_user.user_roles
            if user_role.is_active
        ],
    }