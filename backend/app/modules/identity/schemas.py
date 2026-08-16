"""
========================================================================

LIGHTBURGH EMR

Identity Schemas

========================================================================

Request and response schemas for the Identity module.

Responsibilities
----------------
• User authentication
• User creation
• API response models

========================================================================
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.identity.models import AccountStatus


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


class LoginResponse(BaseModel):
    """
    Response returned after successful authentication.

    Contains the JWT access token, refresh token,
    and token type required for authenticated requests.
    """

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Request payload for refreshing an access token.
    """

    refresh_token: str


# ============================================================================
# User Creation
# ============================================================================


class CreateUserRequest(BaseModel):
    """
    Request payload for creating a user account and assigning
    an initial role.

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
    Minimal user information returned by Identity APIs.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    hospital_id: UUID
    is_superuser: bool
    status: AccountStatus


# ============================================================================
# Role Permission Management
# ============================================================================


class AssignPermissionRequest(BaseModel):
    """
    Request payload for assigning a permission to a role.
    """

    permission_code: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Platform permission code.",
    )


class PermissionResponse(BaseModel):
    """
    Permission returned by the API.
    """

    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str


class RolePermissionsResponse(BaseModel):
    """
    Permissions assigned to a role.
    """

    permissions: list[PermissionResponse]