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

Clinical lifecycle and operational workflow are deliberately separate.

EpisodeStatus represents the clinical lifecycle of the Episode.

EpisodeFlowStatus represents where the Episode currently sits in the
hospital's operational patient-flow process.

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
    Clinical lifecycle status of an Episode of Care.
    """

    OPEN = "OPEN"
    ADMITTED = "ADMITTED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class EpisodeFlowStatus(str, Enum):
    """
    Operational workflow status of an Episode.

    This is deliberately separate from EpisodeStatus.

    EpisodeStatus answers:
        What is the clinical lifecycle of this Episode?

    EpisodeFlowStatus answers:
        Where is this Episode in the hospital's operational
        patient-flow process?
    """

    AWAITING_CHECK_IN = "AWAITING_CHECK_IN"

    WAITING_FOR_NURSING = "WAITING_FOR_NURSING"

    NURSING_IN_PROGRESS = "NURSING_IN_PROGRESS"

    ROUTED = "ROUTED"


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
    # Clinical Status
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
    # Operational Flow Status
    # ------------------------------------------------------------------

    flow_status: Mapped[EpisodeFlowStatus] = mapped_column(
        SqlEnum(
            EpisodeFlowStatus,
            name="episode_flow_status_enum",
        ),
        nullable=False,
        default=EpisodeFlowStatus.AWAITING_CHECK_IN,
        index=True,
    )

    # ------------------------------------------------------------------
    # Reception Check-In
    # ------------------------------------------------------------------

    checked_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    checked_in_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Nursing Workflow
    # ------------------------------------------------------------------

    triaged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    triaged_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    routed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    routed_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
        index=True,
    )

    current_department_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
        index=True,
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

    checked_in_staff: Mapped["Staff | None"] = relationship(
        foreign_keys=[checked_in_by],
    )

    triaged_staff: Mapped["Staff | None"] = relationship(
        foreign_keys=[triaged_by],
    )

    routed_staff: Mapped["Staff | None"] = relationship(
        foreign_keys=[routed_by],
    )

    encounters: Mapped[list["Encounter"]] = relationship(
        back_populates="episode",
    )