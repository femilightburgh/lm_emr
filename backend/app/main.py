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
import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

import app.models
from app.api.router import api_router
from app.bootstrap.startup import bootstrap_application
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging

try:
    # optional: prometheus metrics
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
except Exception:
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # --------------------------------------------------------------
    # Startup
    # --------------------------------------------------------------

    # Configure logging early
    configure_logging()

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

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
    debug=settings.debug,
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in settings.allowed_origins.split(",")
    if origin.strip()
]

if not allowed_origins:
    allowed_origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
    Root endpoint for API discovery.
    """

    return {
        "message": "LIGHTBURGH EMR is running",
        "environment": settings.app_env,
    }


@app.get("/health")
def health():
    """
    Production health check endpoint used by deployment and monitoring.
    """

    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint (if prometheus-client is installed)."""

    if not generate_latest:
        return PlainTextResponse("metrics library not installed", status_code=501)

    data = generate_latest()
    return PlainTextResponse(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/health/db")
def health_db():
    """Health check that validates database connectivity."""

    try:
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute("SELECT 1")

        return {"status": "ok", "db": "reachable"}
    except Exception as exc:  # pragma: no cover - runtime check
        logging.getLogger(__name__).exception("DB health check failed")
        return {"status": "error", "db": "unreachable", "error": str(exc)}