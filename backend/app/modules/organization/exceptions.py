"""
LIGHTBURGH EMR

Organization Exceptions

Application-specific exceptions for organizational entities.
"""

from app.core.exceptions import AppError


class OrganizationError(AppError):
    """
    Base exception for Organization errors.
    """


class DepartmentNotFoundError(OrganizationError):
    """
    Raised when a department cannot be found.
    """

    status_code = 404
    error_code = "DEPARTMENT_NOT_FOUND"


class DepartmentInactiveError(OrganizationError):
    """
    Raised when an operation requires an active department.
    """

    status_code = 409
    error_code = "DEPARTMENT_INACTIVE"