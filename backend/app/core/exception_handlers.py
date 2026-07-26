"""
==============================================================================
LIGHTBURGH EMR

Global Exception Handlers

==============================================================================

Registers global exception handlers used throughout the application.

Business exceptions are translated into standardized API responses.

==============================================================================
"""

from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI

from app.core.exceptions import AppError
from app.core.schemas import ErrorDetail, ErrorResponse


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    """
    Handle all application-specific exceptions.
    """

    response = ErrorResponse(
        error=ErrorDetail(
            code=exc.error_code,
            message=exc.message,
        ),
        trace_id=uuid4(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers.

    This function centralizes the registration of application-wide
    exception handlers during application startup.
    """

    app.add_exception_handler(
        AppError,
        app_error_handler,
    )