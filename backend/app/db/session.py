"""
========================================================================

LIGHTBURGH EMR

Database Session Management

========================================================================

Purpose
-------

This module configures SQLAlchemy's database engine and provides
database sessions to the rest of the application.

Responsibilities
----------------

• Create the SQLAlchemy engine
• Configure the session factory
• Provide FastAPI dependency injection for database sessions

========================================================================
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import os

from app.core.config import settings

import app.models  # ensure all ORM models are imported so SQLAlchemy registers mappers


# ----------------------------------------------------------------------
# Database Engine
# ----------------------------------------------------------------------

_database_url = os.environ.get("TEST_DATABASE_URL") or settings.database_url

engine = create_engine(
    _database_url,
    echo=True,
    pool_pre_ping=True,
)

# When using SQLite for tests/local dev, ensure Python uuid.UUID objects can be
# adapted to strings for parameter binding.
if _database_url.startswith("sqlite"):
    try:
        import sqlite3
        import uuid

        sqlite3.register_adapter(uuid.UUID, lambda u: str(u))
    except Exception:
        # non-blocking: if registration fails, tests may fail and surface the
        # underlying issue.
        pass


# ----------------------------------------------------------------------
# Session Factory
# ----------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ----------------------------------------------------------------------
# FastAPI Database Dependency
# ----------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for a single request.

    A new SQLAlchemy session is created at the beginning of the request
    and automatically closed when the request finishes, regardless of
    whether it succeeds or fails.

    Usage
    -----
    Used with FastAPI dependency injection:

        db: Session = Depends(get_db)
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()