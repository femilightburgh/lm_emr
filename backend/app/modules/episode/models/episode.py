"""
==============================================================================
LIGHTBURGH EMR

Episode Model
==============================================================================

An Episode of Care represents a patient's healthcare journey for a
specific clinical problem.

An Episode:

• Belongs to exactly one Hospital.
• Belongs to exactly one Patient.
• Has one managing doctor once admitted.
• Groups related Encounters.
• Groups related Clinical Events.
• Represents the root aggregate of a patient's healthcare journey.

Episode numbers are unique within a Hospital.

==============================================================================
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.modules.encounter.models import Encounter
    from app.modules.organization.models import Hospital
    from app.modules.patients.models import Patient
    from app.modules.staff.models import Staff


class EpisodeStatus(str, Enum):
    """
    Status of an Episode of Care.
    """

    OPEN = "OPEN"
    ADMITTED = "ADMITTED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Episode(BaseEntity):
    """
    Represents an Episode of Care.

    An Episode groups all clinical activity associated with a
    single healthcare journey.

    Once an Episode is admitted, the clinician who performs the
    admission becomes the managing doctor for that Episode.
    """

    __tablename__ = "episodes"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "episode_number",
            name="uq_episodes_hospital_episode_number",
        ),
    )

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------

    hospital_id: Mapped[UUID] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Managing Doctor
    # ------------------------------------------------------------------

    managing_doctor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    episode_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status: Mapped[EpisodeStatus] = mapped_column(
        SqlEnum(
            EpisodeStatus,
            name="episode_status_enum",
        ),
        nullable=False,
        default=EpisodeStatus.OPEN,
    )

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    hospital: Mapped["Hospital"] = relationship(
        back_populates="episodes",
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="episodes",
    )

    managing_doctor: Mapped["Staff | None"] = relationship(
        foreign_keys=[managing_doctor_id],
    )

    encounters: Mapped[list["Encounter"]] = relationship(
        back_populates="episode",
    )