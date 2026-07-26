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

from app.core.config import settings


# ----------------------------------------------------------------------
# Database Engine
# ----------------------------------------------------------------------

engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
)


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