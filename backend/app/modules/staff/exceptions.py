"""
==============================================================================
LIGHTBURGH EMR

Staff Exceptions

==============================================================================

Custom exceptions raised by the Staff module.

The service layer raises these exceptions to communicate business errors.
The API layer is responsible for translating them into HTTP responses.

==============================================================================
"""

from app.core.exceptions import AppError


class StaffError(AppError):
    """Base exception for all staff-related errors."""


class StaffNotFoundError(StaffError):
    """
    Raised when a staff member cannot be found.
    """

    status_code = 404
    error_code = "STAFF_NOT_FOUND"


class DuplicateStaffNumberError(StaffError):
    """Raised when a staff number already exists within a hospital."""


class HospitalNotFoundError(StaffError):
    """Raised when the specified hospital does not exist."""


class InvalidEmploymentDateError(StaffError):
    """Raised when employment dates violate business rules."""


class NoCurrentEmploymentError(StaffError):
    """
    Raised when an operation requires an active employment period
    but none exists.
    """