"""
==============================================================================
LIGHTBURGH EMR

Medication Dose Model
==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base_entity import BaseEntity
from app.modules.clinical_orders.enums import (
    MedicationDoseStatus,
)


if TYPE_CHECKING:
    from app.modules.clinical_orders.models.medication_treatment import (
        MedicationTreatment,
    )
    from app.modules.clinical_orders.models.medication_administration import (
        MedicationAdministration,
    )


class MedicationDose(BaseEntity):
    """
    Represents one scheduled dose within an inpatient medication treatment.
    """

    __tablename__ = "medication_doses"

    __table_args__ = (
        UniqueConstraint(
            "treatment_id",
            "scheduled_at",
            name="uq_medication_dose_treatment_time",
        ),
    )

    treatment_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "medication_treatments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    status: Mapped[MedicationDoseStatus] = mapped_column(
        SqlEnum(
            MedicationDoseStatus,
            name="medication_dose_status_enum",
        ),
        nullable=False,
        default=MedicationDoseStatus.PENDING,
        index=True,
    )

    treatment: Mapped["MedicationTreatment"] = relationship(
        back_populates="doses",
    )

    administration: Mapped[
        "MedicationAdministration | None"
    ] = relationship(
        back_populates="dose",
        uselist=False,
        cascade="all, delete-orphan",
    )
