"""
==============================================================================
LIGHTBURGH EMR

Alembic Environment Configuration

==============================================================================

Purpose
-------
This module configures Alembic for database migrations.

Responsibilities:

    • Load SQLAlchemy metadata.
    • Register every ORM model.
    • Configure offline migrations.
    • Configure online migrations.

IMPORTANT
---------
All ORM models are imported through app.models.

This ensures:

    • SQLAlchemy relationships are registered.
    • Base.metadata contains every table.
    • Alembic autogeneration works correctly.

When adding a new module, you only need to import it inside
app/models/__init__.py.

No changes to this file should be necessary.

==============================================================================
"""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.db.base import Base

# ---------------------------------------------------------------------------
# Register all ORM models
# ---------------------------------------------------------------------------

import app.models  # noqa: F401

# ---------------------------------------------------------------------------
# Alembic Configuration
# ---------------------------------------------------------------------------

config = context.config

test_database_url = context.get_x_argument(
    as_dictionary=True
).get("test_database_url")

if test_database_url:
    config.set_main_option(
        "sqlalchemy.url",
        test_database_url,
    )

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline Migrations
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Execute migrations without creating a database connection.

    Offline migrations generate SQL scripts instead of executing
    SQL directly against a database.
    """

    url = (
        os.environ.get("TEST_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or config.get_main_option("sqlalchemy.url")
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online Migrations
# ---------------------------------------------------------------------------

def run_migrations_online() -> None:
    """
    Execute migrations against a live database connection.

    Database URL priority:
      1. TEST_DATABASE_URL, when provided.
      2. DATABASE_URL, when provided.
      3. sqlalchemy.url from alembic.ini as a fallback.
    """

    database_url = (
        os.environ.get("TEST_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or config.get_main_option("sqlalchemy.url")
    )

    connectable = engine_from_config(
        {"sqlalchemy.url": database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()