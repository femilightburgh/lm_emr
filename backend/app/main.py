"""
========================================================================

LIGHTBURGH EMR

Application Entry Point

========================================================================

Purpose
-------

Initializes the FastAPI application and registers the central API router.

Business modules should NOT be imported directly into this file.
Instead, they should be registered through app.api.router.

========================================================================
"""

from fastapi import FastAPI

import app.models
from app.api.router import api_router
from app.core.exception_handlers import register_exception_handlers


app = FastAPI(
    title="LIGHTBURGH EMR API",
    version="1.0.0",
    description="Backend API",
)

register_exception_handlers(app)

# ----------------------------------------------------------------------
# Register API Routers
# ----------------------------------------------------------------------

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    """
    Health check endpoint.
    """

    return {
        "message": "LIGHTBURGH EMR is running",
    }