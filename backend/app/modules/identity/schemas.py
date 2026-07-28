"""
========================================================================

LIGHTBURGH EMR

Identity Schemas

========================================================================

Purpose
-------

Pydantic schemas define the structure of data entering and leaving
the Identity module.

Responsibilities
----------------

• Validate incoming API requests
• Validate outgoing API responses
• Generate OpenAPI / Swagger documentation
• Prevent invalid data from reaching business logic

========================================================================
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Request payload for user authentication.

    Since LIGHTBURGH is a multi-tenant platform,
    users authenticate using:

    • Hospital Code
    • Email Address
    • Password

    This ensures identical email addresses can exist
    across different hospitals.
    """

    hospital_code: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Unique hospital code.",
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        description="User password.",
    )


class TokenResponse(BaseModel):
    """
    Response returned after successful authentication.
    """

    access_token: str

    refresh_token: str

    token_type: str = "Bearer"


class UserSummary(BaseModel):
    """
    Minimal user information returned by APIs.

    This schema intentionally excludes sensitive
    information such as passwords.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    email: EmailStr

    hospital_id: UUID

    is_superuser: bool