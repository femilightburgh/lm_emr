"""
==============================================================================
LIGHTBURGH EMR

SQLAlchemy Declarative Base

==============================================================================

Purpose
-------
This module defines the application's root SQLAlchemy declarative base.

Every ORM model in LIGHTBURGH ultimately inherits from this base through
`BaseEntity`.

Responsibilities
----------------
• Provide the SQLAlchemy metadata registry.
• Serve as the root class for all ORM models.
• Supply metadata used by Alembic for schema generation.

Notes
-----
Do NOT place reusable entity fields (id, timestamps, audit fields, etc.)
in this module.

Those belong in `BaseEntity`, which extends this base.

Keeping the registry (`Base`) separate from the common entity model
(`BaseEntity`) makes the architecture easier to understand and maintain.

==============================================================================
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Root declarative base for all SQLAlchemy ORM models.

    SQLAlchemy collects metadata from every model that ultimately
    inherits from this class.
    """

    pass