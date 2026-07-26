"""
========================================================================

LIGHTBURGH EMR

Global Exception Handlers

========================================================================

Purpose
-------

Converts business exceptions into HTTP responses.

Business services raise exceptions.

FastAPI automatically converts them into JSON responses.

========================================================================
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import (
    AccountLockedException,
    DuplicateResourceException,
    InvalidCredentialsException,
    PermissionDeniedException,
    ResourceNotFoundException,
)


def register_exception_handlers(app: FastAPI):
    """
    Register all global exception handlers.
    """

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsException,
    ):
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid email or password."
            },
        )

    @app.exception_handler(AccountLockedException)
    async def account_locked_handler(
        request: Request,
        exc: AccountLockedException,
    ):
        return JSONResponse(
            status_code=423,
            content={
                "detail": "Account has been locked."
            },
        )

    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_handler(
        request: Request,
        exc: ResourceNotFoundException,
    ):
        return JSONResponse(
            status_code=404,
            content={
                "detail": "Resource not found."
            },
        )

    @app.exception_handler(DuplicateResourceException)
    async def duplicate_resource_handler(
        request: Request,
        exc: DuplicateResourceException,
    ):
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Resource already exists."
            },
        )

    @app.exception_handler(PermissionDeniedException)
    async def permission_denied_handler(
        request: Request,
        exc: PermissionDeniedException,
    ):
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Permission denied."
            },
        )