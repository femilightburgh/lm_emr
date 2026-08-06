"""
========================================================================

LIGHTBURGH EMR

Identity API Router

========================================================================

This router exposes authentication endpoints.

Business logic belongs in AuthService.

Database access belongs in repositories.

The router should remain as thin as possible.

========================================================================
"""

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.identity.auth_service import AuthService
from app.modules.identity.exceptions import (
    InactiveAccountError,
    InvalidCredentialsError,
)
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import (
    CreateUserRequest,
    LoginRequest,
    LoginResponse,
    UserResponse,
)
from app.modules.identity.token_service import TokenService
from app.modules.identity.user_service import UserService

from app.core.security.dependencies import get_current_user

from app.core.security.authorization import require_role

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


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
    Create a new user account.
    """

    repository = IdentityRepository(db)
    service = UserService(repository)

    user = service.create_user(
        hospital_code=request.hospital_code,
        email=request.email,
        password=request.password,
        role_name=request.role_name,
    )

    repository.save()
    repository.refresh(user)

    return UserResponse.model_validate(user)


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

    This endpoint exists for Swagger UI and OAuth2-compatible clients.
    It delegates authentication to the existing AuthService.
    """

    repository = IdentityRepository(db)
    token_service = TokenService()

    service = AuthService(
        repository=repository,
        token_service=token_service,
    )

    #
    # OAuth2 provides only "username".
    #
    # LIGHTBURGH expects hospital_code + email.
    #
    # For now we encode them as:
    #
    #     username = hospital_code|email
    #
    # Example:
    #
    #     WTH001|admin@lightburgh.com
    #


    try:
        hospital_code, email = form_data.username.split("|", maxsplit=1)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Username must be in the format "
                "'hospital_code|email'."
            ),
        )

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


@router.get(
    "/me",
    summary="Current authenticated user",
)
def me(
    current_user=Depends(require_role("Administrator")),
):
    """
    Test role-based authorization.
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