from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.diagnoses.enums import (
    DiagnosisCertainty,
    DiagnosisType,
)

if TYPE_CHECKING:
    from app.modules.encounter.models import Encounter
    from app.modules.episode.models import Episode
    from app.modules.staff.models import Staff


class ClinicalDiagnosis(BaseEntity):
    """
    A structured clinical diagnosis recorded during patient care.
    """

    __tablename__ = "clinical_diagnoses"

    encounter_id: Mapped[UUID] = mapped_column(
        ForeignKey("encounters.id"),
        nullable=False,
        index=True,
    )

    episode_id: Mapped[UUID] = mapped_column(
        ForeignKey("episodes.id"),
        nullable=False,
        index=True,
    )

    diagnosis_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    code_system: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    diagnosis_type: Mapped[DiagnosisType] = mapped_column(
        SqlEnum(
            DiagnosisType,
            name="diagnosis_type_enum",
        ),
        nullable=False,
        index=True,
    )

    certainty: Mapped[DiagnosisCertainty] = mapped_column(
        SqlEnum(
            DiagnosisCertainty,
            name="diagnosis_certainty_enum",
        ),
        nullable=False,
        index=True,
    )

    onset_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    diagnosed_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    diagnosed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    encounter: Mapped["Encounter"] = relationship()
    episode: Mapped["Episode"] = relationship()
    diagnosing_staff: Mapped["Staff"] = relationship(
        foreign_keys=[diagnosed_by],
    )
