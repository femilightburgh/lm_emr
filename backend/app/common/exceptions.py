"""
========================================================================

LIGHTBURGH EMR

Common Exceptions

========================================================================

Purpose
-------

Contains reusable business exceptions shared across all modules.

Business logic raises these exceptions.

Routers translate them into HTTP responses.

========================================================================
"""


class LightburghException(Exception):
    """
    Base class for all application exceptions.
    """

    pass


class InvalidCredentialsException(LightburghException):
    """
    Raised when authentication credentials are invalid.
    """

    pass


class AccountLockedException(LightburghException):
    """
    Raised when a user account has been locked.
    """

    pass


class ResourceNotFoundException(LightburghException):
    """
    Raised when a requested resource does not exist.
    """

    pass


class DuplicateResourceException(LightburghException):
    """
    Raised when attempting to create a duplicate resource.
    """

    pass


class PermissionDeniedException(LightburghException):
    """
    Raised when a user lacks permission.
    """

    pass