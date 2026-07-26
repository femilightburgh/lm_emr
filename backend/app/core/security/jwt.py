"""
========================================================================

LIGHTBURGH EMR

JWT Utility Functions

========================================================================

Purpose
-------

This module provides low-level functionality for creating and
verifying JSON Web Tokens (JWTs).

JWTs are digitally signed tokens used to authenticate users after
they successfully log in.

This module deliberately contains only JWT-related operations.

It does NOT:

- Verify passwords
- Authenticate users
- Query the database

Those responsibilities belong elsewhere.

========================================================================
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings


def create_token(
    *,
    subject: str,
    expires_delta: timedelta,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT.

    Parameters
    ----------
    subject:
        The primary identity represented by this token.
        For LIGHTBURGH this will normally be the UserAccount ID.

    expires_delta:
        Duration before the token expires.

    additional_claims:
        Optional extra claims to include in the payload.
        Examples:
            hospital_id
            roles
            token_type

    Returns
    -------
    str
        Encoded JWT string.
    """

    now = datetime.now(UTC)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT.

    Raises
    ------
    jwt.InvalidTokenError
        If the token is invalid or expired.
    """

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )