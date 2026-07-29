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