"""
========================================================================

LIGHTBURGH EMR

Identity Schemas

========================================================================
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================================
# Authentication
# ============================================================================


class LoginRequest(BaseModel):
    """
    Request payload for user authentication.
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


# ============================================================================
# User Creation
# ============================================================================


class CreateUserRequest(BaseModel):
    """
    Generic request for creating a user and assigning an initial role.

    This schema is intentionally generic so it can be reused for:

    • Hospital Administrator
    • Doctor
    • Nurse
    • Pharmacist
    • Cashier
    • Laboratory Scientist
    • Radiographer
    • Any future staff role
    """

    hospital_code: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Hospital code.",
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        description="User password.",
    )

    role_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Role to assign.",
    )


# ============================================================================
# Responses
# ============================================================================


class UserResponse(BaseModel):
    """
    Minimal user information returned by APIs.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    hospital_id: UUID
    is_superuser: bool
    status: str