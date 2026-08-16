"""
==============================================================================
LIGHTBURGH EMR

Encounter Model

==============================================================================

An Encounter represents one professional's attendance to a patient
within an Episode of Care.

An Encounter:

• Belongs to exactly one Episode.
• Belongs to exactly one Staff member.
• Represents one professional attendance.
• May contain multiple Clinical Events.
• Has an explicit lifecycle from OPEN to CLOSED.

Clinical activity belongs to Events rather than directly to the Encounter.

==============================================================================
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity


if TYPE_CHECKING:
    from app.modules.episode.models import Episode
    from app.modules.events.models import ClinicalEvent
    from app.modules.staff.models import Staff
    from app.modules.clinical_documents.models import ClinicalDocument


class EncounterStatus(str, Enum):
    """
    Lifecycle status of an Encounter.
    """

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Encounter(BaseEntity):
    """
    Represents one professional attendance to a patient
    within an Episode of Care.
    """

    __tablename__ = "encounters"

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------

    episode_id: Mapped[UUID] = mapped_column(
        ForeignKey("episodes.id"),
        nullable=False,
        index=True,
    )

    staff_id: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Encounter Information
    # ------------------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[EncounterStatus] = mapped_column(
        SqlEnum(
            EncounterStatus,
            name="encounter_status_enum",
        ),
        nullable=False,
        default=EncounterStatus.OPEN,
    )

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    episode: Mapped["Episode"] = relationship(
        back_populates="encounters",
    )

    staff: Mapped["Staff"] = relationship(
        back_populates="encounters",
    )

    events: Mapped[list["ClinicalEvent"]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
    )

    clinical_documents: Mapped[list["ClinicalDocument"]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
    )