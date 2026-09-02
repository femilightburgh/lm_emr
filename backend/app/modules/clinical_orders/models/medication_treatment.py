"""
==============================================================================
LIGHTBURGH EMR

Medication Treatment Model
==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base_entity import BaseEntity
from app.modules.clinical_orders.enums import (
    MedicationTreatmentStatus,
)


if TYPE_CHECKING:
    from app.modules.episode.models import Episode
    from app.modules.clinical_orders.models.prescription import Prescription
    from app.modules.staff.models import Staff
    from app.modules.clinical_orders.models.medication_dose import (
        MedicationDose,
    )


class MedicationTreatment(BaseEntity):
    """
    Represents an inpatient medication treatment derived from a
    structured Prescription.
    """

    __tablename__ = "medication_treatments"

    __table_args__ = (
        UniqueConstraint(
            "prescription_id",
            name="uq_medication_treatment_prescription",
        ),
    )

    prescription_id: Mapped[UUID] = mapped_column(
        ForeignKey("prescriptions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    episode_id: Mapped[UUID] = mapped_column(
        ForeignKey("episodes.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[MedicationTreatmentStatus] = mapped_column(
        SqlEnum(
            MedicationTreatmentStatus,
            name="medication_treatment_status_enum",
        ),
        nullable=False,
        default=MedicationTreatmentStatus.ACTIVE,
        index=True,
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    discontinued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    discontinued_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
    )

    discontinued_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    prescription: Mapped["Prescription"] = relationship()

    episode: Mapped["Episode"] = relationship()

    discontinuing_staff: Mapped["Staff | None"] = relationship(
        foreign_keys=[discontinued_by],
    )

    doses: Mapped[list["MedicationDose"]] = relationship(
        back_populates="treatment",
        cascade="all, delete-orphan",
        order_by="MedicationDose.scheduled_at",
    )
