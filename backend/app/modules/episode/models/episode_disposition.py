"""
==============================================================================
LIGHTBURGH EMR

Episode Disposition Model

==============================================================================

Purpose
-------
Stores a clinical disposition decision made during an Episode of Care.

Responsibilities
----------------
- Preserve the disposition selected by the clinician.
- Associate the decision with the Episode and Encounter.
- Record the clinician who made the decision.
- Preserve optional clinical details.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity


if TYPE_CHECKING:
    from app.modules.encounter.models import Encounter
    from app.modules.episode.models.episode import Episode
    from app.modules.organization.models import Hospital
    from app.modules.staff.models import Staff


class EpisodeDispositionType(str, Enum):
    """
    Clinical disposition selected for an Episode.
    """

    CONTINUE_ADMISSION = "CONTINUE_ADMISSION"
    DISCHARGE = "DISCHARGE"
    TRANSFER = "TRANSFER"
    REFERRAL = "REFERRAL"
    OTHER = "OTHER"


class EpisodeDisposition(BaseEntity):
    """
    Records one clinical disposition decision for an Episode.
    """

    __tablename__ = "episode_dispositions"

    hospital_id: Mapped[UUID] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    episode_id: Mapped[UUID] = mapped_column(
        ForeignKey("episodes.id"),
        nullable=False,
        index=True,
    )

    encounter_id: Mapped[UUID] = mapped_column(
        ForeignKey("encounters.id"),
        nullable=False,
        index=True,
    )

    disposition: Mapped[EpisodeDispositionType] = mapped_column(
        SqlEnum(
            EpisodeDispositionType,
            name="episode_disposition_type_enum",
        ),
        nullable=False,
        index=True,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decided_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    hospital: Mapped["Hospital"] = relationship()

    episode: Mapped["Episode"] = relationship(
        back_populates="dispositions",
    )

    encounter: Mapped["Encounter"] = relationship()

    deciding_staff: Mapped["Staff"] = relationship(
        foreign_keys=[decided_by],
    )
