"""
========================================================================

LIGHTBURGH EMR

Token Service

========================================================================

Responsible for creating and validating JWT tokens.

This service contains NO database logic.

========================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import settings


class TokenService:
    """
    Service responsible for JWT creation and validation.
    """
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"

    CLAIM_SUBJECT = "sub"
    CLAIM_HOSPITAL_ID = "hospital_id"
    CLAIM_ROLES = "roles"
    CLAIM_TOKEN_TYPE = "type"
    CLAIM_ISSUED_AT = "iat"
    CLAIM_EXPIRATION = "exp"
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = (
            settings.access_token_expire_minutes
        )
        self.refresh_token_expire_days = (
            settings.refresh_token_expire_days
        )

    def _encode_token(self, payload: dict) -> str:
        """
        Encode and sign a JWT payload.
        """

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )


    def create_access_token(
        self,
        *,
        user_id: UUID,
        hospital_id: UUID,
        roles: list[str],
    ) -> str:
        """
        Create a signed JWT access token.
        """

        issued_at = datetime.now(UTC)

        expires_at = issued_at + timedelta(
            minutes=self.access_token_expire_minutes
        )

        payload = {
            self.CLAIM_SUBJECT: str(user_id),
            self.CLAIM_HOSPITAL_ID: str(hospital_id),
            self.CLAIM_ROLES: roles,
            self.CLAIM_TOKEN_TYPE: self.ACCESS_TOKEN,
            self.CLAIM_ISSUED_AT: issued_at,
            self.CLAIM_EXPIRATION: expires_at,
        }

        return self._encode_token(payload)
    

    def create_refresh_token(
        self,
        *,
        user_id: UUID,
    ) -> str:
        """
        Create a signed JWT refresh token.
        """

        issued_at = datetime.now(UTC)

        expires_at = issued_at + timedelta(
            days=self.refresh_token_expire_days
        )

        payload = {
            self.CLAIM_SUBJECT: str(user_id),
            self.CLAIM_TOKEN_TYPE: self.REFRESH_TOKEN,
            self.CLAIM_ISSUED_AT: issued_at,
            self.CLAIM_EXPIRATION: expires_at,
        }

        return self._encode_token(payload)
    
    def decode_token(self, token: str) -> dict:
        """
        Decode and validate a JWT.
        """

        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
        )