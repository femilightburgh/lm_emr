"""
==============================================================================
LIGHTBURGH EMR

Application Exceptions

==============================================================================

Defines the base exception hierarchy for the application.

Business exceptions inherit from AppError and remain independent of HTTP.
Global exception handlers translate these exceptions into API responses.

==============================================================================
"""


class AppError(Exception):
    """
    Base class for all application-specific exceptions.

    Attributes
    ----------
    message:
        Human-readable explanation of the error.

    error_code:
        Stable machine-readable error code.

    status_code:
        HTTP status code returned by the API.
    """

    status_code: int = 400
    error_code: str = "APPLICATION_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)