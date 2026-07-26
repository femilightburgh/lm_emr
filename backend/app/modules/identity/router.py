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
from app.modules.identity.schemas import (
    LoginRequest,
    TokenResponse,
)
from app.modules.identity.service import AuthenticationService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


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