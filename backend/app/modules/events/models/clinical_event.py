"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Model
==============================================================================

Represents a clinical action performed or recorded during an Encounter.

Clinical hierarchy
------------------
Patient
    ↓
Episode of Care
    ↓
Encounter
    ↓
Clinical Event

An Event belongs to exactly one Encounter.

Responsibilities
----------------
• Record the type of clinical action.
• Record the professional who performed the action.
• Record when the action occurred.
• Store event-specific structured data.
• Preserve the relationship to the Encounter.

==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.events.enums import EventType

if TYPE_CHECKING:
    from app.modules.encounter.models import Encounter
    from app.modules.staff.models import Staff


class ClinicalEvent(BaseEntity):
    """
    Represents a clinical action performed during an Encounter.
    """

    __tablename__ = "clinical_events"

    # ------------------------------------------------------------------
    # Encounter
    # ------------------------------------------------------------------

    encounter_id: Mapped[UUID] = mapped_column(
        ForeignKey("encounters.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Event Information
    # ------------------------------------------------------------------

    event_type: Mapped[EventType] = mapped_column(
        Enum(
            EventType,
            name="clinical_event_type_enum",
        ),
        nullable=False,
        index=True,
    )
    performed_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    encounter: Mapped["Encounter"] = relationship(
        back_populates="events",
    )

    performer: Mapped["Staff"] = relationship()