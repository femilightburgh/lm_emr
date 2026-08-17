"""
==============================================================================
LIGHTBURGH EMR

Identity Exceptions

==============================================================================

Custom exceptions raised by the Identity module.

==============================================================================
"""

from app.core.exceptions import AppError


class IdentityError(AppError):
    """
    Base exception for Identity.
    """


# ============================================================================
# Hospital / User
# ============================================================================


class HospitalNotFoundError(IdentityError):
    status_code = 404
    error_code = "HOSPITAL_NOT_FOUND"


class UserAlreadyExistsError(IdentityError):
    status_code = 409
    error_code = "USER_ALREADY_EXISTS"


# ============================================================================
# Roles
# ============================================================================


class RoleNotFoundError(IdentityError):
    """
    Raised when a role cannot be found.
    """

    status_code = 404
    error_code = "ROLE_NOT_FOUND"


class RoleAlreadyExistsError(IdentityError):
    """
    Raised when a role with the same name already exists
    within a hospital.
    """

    status_code = 409
    error_code = "ROLE_ALREADY_EXISTS"


class RoleAlreadyAssignedError(IdentityError):
    """
    Raised when a role is already actively assigned to a user.
    """

    status_code = 409
    error_code = "ROLE_ALREADY_ASSIGNED"


class UserRoleNotFoundError(IdentityError):
    """
    Raised when a requested user-role assignment cannot be found.
    """

    status_code = 404
    error_code = "USER_ROLE_NOT_FOUND"


# ============================================================================
# Authentication
# ============================================================================


class InvalidCredentialsError(Exception):
    """
    Raised when authentication credentials are invalid.
    """

    def __init__(self):
        super().__init__(
            "Invalid email or password."
        )


class InactiveAccountError(Exception):
    """
    Raised when a user account is not active.
    """

    def __init__(self):
        super().__init__(
            "User account is not active."
        )


class InvalidTokenError(Exception):
    """
    Raised when a JWT is invalid.
    """

    def __init__(self):
        super().__init__(
            "Invalid authentication token."
        )


class ExpiredTokenError(Exception):
    """
    Raised when a JWT has expired.
    """

    def __init__(self):
        super().__init__(
            "Authentication token has expired."
        )


# ============================================================================
# Permissions
# ============================================================================


class PermissionDeniedError(IdentityError):
    """
    Raised when a user attempts to perform an action
    without the required permission or role.
    """

    status_code = 403
    error_code = "PERMISSION_DENIED"

    def __init__(self):
        super().__init__(
            "You do not have permission to perform this action."
        )


class PermissionNotFoundError(IdentityError):
    """
    Raised when a permission cannot be found.
    """

    status_code = 404
    error_code = "PERMISSION_NOT_FOUND"