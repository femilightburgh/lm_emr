"""
========================================================================

LIGHTBURGH EMR

Token Service

========================================================================

Purpose
-------

This module provides high-level functions for issuing JWTs used by the
authentication system.

Unlike jwt.py, which only knows how to encode and decode JWT payloads,
this module knows what information LIGHTBURGH wants to place inside its
tokens.

Responsibilities
----------------

• Create Access Tokens
• Create Refresh Tokens

This separation keeps business rules independent from JWT mechanics.

========================================================================
"""

from datetime import timedelta
from uuid import UUID, uuid4

from app.core.config import settings
from app.core.security.jwt import create_token


def create_access_token(
    *,
    user_id: UUID,
    hospital_id: UUID,
) -> str:
    """
    Create a short-lived access token.

    Access tokens are sent with every authenticated API request.
    """

    return create_token(
        subject=str(user_id),
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        ),
        additional_claims={
            "hospital_id": str(hospital_id),
            "token_type": "access",
            "jti": str(uuid4()),
            "iss": settings.app_name,
            "aud": "lightburgh-api",
        },
    )


def create_refresh_token(
    *,
    user_id: UUID,
    hospital_id: UUID,
) -> str:
    """
    Create a long-lived refresh token.

    Refresh tokens are only used to obtain new access tokens after an
    access token expires.
    """

    return create_token(
        subject=str(user_id),
        expires_delta=timedelta(
            days=settings.refresh_token_expire_days
        ),
        additional_claims={
            "hospital_id": str(hospital_id),
            "token_type": "refresh",
            "jti": str(uuid4()),
            "iss": settings.app_name,
            "aud": "lightburgh-api",
        },
    )