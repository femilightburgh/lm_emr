"""
========================================================================

LIGHTBURGH EMR

Security Dependencies

========================================================================

Purpose
-------

Reusable FastAPI dependencies for authentication and authorization.

========================================================================
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.modules.identity.token_service import TokenService
from app.db.session import get_db
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.models import UserAccount

# ----------------------------------------------------------------------
# OAuth2 Password Bearer
# ----------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
)


def get_bearer_token(
    token: str = Depends(oauth2_scheme),
) -> str:
    """
    Extract the bearer token from the Authorization header.
    """

    return token


def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> UserAccount:
    """
    Validate the JWT and return the authenticated user.
    """

    token_service = TokenService()

    try:
        payload = token_service.decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token.",
            )

        user_id = payload["sub"]

        repository = IdentityRepository(db)

        user = repository.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        return user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )