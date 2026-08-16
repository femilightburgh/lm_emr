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

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.api.router import api_router
from app.bootstrap.startup import bootstrap_application
from app.core.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # --------------------------------------------------------------
    # Startup
    # --------------------------------------------------------------

    bootstrap_application()

    yield

    # --------------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------------

    # Future cleanup goes here.


app = FastAPI(
    title="LIGHTBURGH EMR API",
    version="1.0.0",
    description="Backend API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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