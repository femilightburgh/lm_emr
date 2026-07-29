"""
========================================================================

LIGHTBURGH EMR

Identity API Router

========================================================================

This router exposes all authentication endpoints.

Business rules belong in AuthenticationService.

Database access belongs in repositories.

The router should remain as thin as possible.

========================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.user_service import UserService
from app.modules.identity.schemas import (
    CreateUserRequest,
    UserResponse,
    LoginRequest,
    TokenResponse,
)
from app.modules.identity.service import AuthenticationService

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

    This endpoint only creates the user.
    Role assignment is handled separately.
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
    response_model=TokenResponse,
    summary="Authenticate a user",
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return JWT tokens.
    """

    service = AuthenticationService(db)

    tokens = service.authenticate(
        hospital_code=request.hospital_code,
        email=request.email,
        password=request.password,
    )

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials.",
        )

    return tokens