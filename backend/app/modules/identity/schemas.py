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

from datetime import datetime
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


class UserRoleResponse(BaseModel):
    """
    Role assignment returned by the Administration API.
    """

    id: UUID
    role_id: UUID
    role_name: str
    is_active: bool


class AdminUserResponse(BaseModel):
    """
    User representation returned to the Administration workspace.
    """

    id: UUID
    email: EmailStr
    hospital_id: UUID
    is_superuser: bool
    status: AccountStatus
    roles: list[UserRoleResponse]


class CreateStaffRequest(BaseModel):
    """
    Request payload for administrator-led staff onboarding.

    The administrator supplies the staff member's email and
    initial role. The staff member creates their own password
    during account activation.
    """

    email: EmailStr

    role_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Initial role to assign.",
    )


class CreateStaffResponse(BaseModel):
    """
    Response returned after administrator-led staff onboarding.
    """

    user: AdminUserResponse

    invitation_token: str
    invitation_expires_at: datetime


class ActivateUserRequest(BaseModel):
    """
    Request payload for activating a pending user account.
    """

    token: str = Field(
        ...,
        min_length=20,
        description="One-time invitation token.",
    )

    password: str = Field(
        ...,
        min_length=8,
        description="The user's new password.",
    )

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


# ============================================================================
# Role Management
# ============================================================================


class CreateRoleRequest(BaseModel):
    """
    Request payload for creating a hospital role.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable role name.",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the role.",
    )


class UpdateRoleRequest(BaseModel):
    """
    Request payload for updating a hospital role.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable role name.",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the role.",
    )


class RoleResponse(BaseModel):
    """
    Role returned by the Administration API.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    hospital_id: UUID
    name: str
    description: str | None
    is_template: bool


class AssignRoleRequest(BaseModel):
    """
    Request payload for assigning a role to a user.
    """

    role_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Role to assign to the user.",
    )