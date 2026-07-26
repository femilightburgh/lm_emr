"""
==============================================================================
LIGHTBURGH EMR

Base Entity

==============================================================================

Purpose
-------
Defines the common entity inherited by every persistent ORM model.

Rather than repeating common columns across every model, BaseEntity
provides a shared implementation for:

    • Primary key (UUID)
    • Record creation timestamp
    • Record update timestamp

Architecture
------------
Every database entity in LIGHTBURGH ultimately inherits from:

    Base
        └── BaseEntity
                ├── Hospital
                ├── UserAccount
                ├── Staff
                ├── Patient
                ├── Appointment
                ├── Encounter
                └── ...

This keeps all common persistence behaviour in a single place while
allowing domain models to focus solely on business data.

Notes
-----
• BaseEntity is abstract and therefore does not create a database table.
• UUIDs are generated automatically.
• Timestamps are timezone-aware (UTC).
• The updated_at field is automatically refreshed whenever the row is
  modified.

==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BaseEntity(Base):
    """
    Abstract base class inherited by all persistent ORM entities.

    Every model that represents a database table should inherit from
    BaseEntity instead of directly inheriting from Base.
    """

    __abstract__ = True

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Globally unique identifier for the entity.",
    )

    # ------------------------------------------------------------------
    # Audit Fields
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        doc="UTC timestamp indicating when the record was created.",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        doc="UTC timestamp automatically updated whenever the record changes.",
    )