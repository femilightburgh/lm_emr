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
    """Base exception for Identity."""


class HospitalNotFoundError(IdentityError):
    status_code = 404
    error_code = "HOSPITAL_NOT_FOUND"


class UserAlreadyExistsError(IdentityError):
    status_code = 409
    error_code = "USER_ALREADY_EXISTS"


class RoleNotFoundError(IdentityError):
    status_code = 404
    error_code = "ROLE_NOT_FOUND"


class InvalidCredentialsError(Exception):
    """
    Raised when authentication credentials are invalid.
    """

    def __init__(self):
        super().__init__("Invalid email or password.")


class InactiveAccountError(Exception):
    """
    Raised when a user account is not active.
    """

    def __init__(self):
        super().__init__("User account is not active.")


class InvalidTokenError(Exception):
    """
    Raised when a JWT is invalid.
    """

    def __init__(self):
        super().__init__("Invalid authentication token.")


class ExpiredTokenError(Exception):
    """
    Raised when a JWT has expired.
    """

    def __init__(self):
        super().__init__("Authentication token has expired.")