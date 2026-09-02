"""
==============================================================================
LIGHTBURGH EMR

Medication Administration Model
==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base_entity import BaseEntity
from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
)


if TYPE_CHECKING:
    from app.modules.clinical_orders.models.medication_dose import (
        MedicationDose,
    )
    from app.modules.staff.models import Staff


class MedicationAdministration(BaseEntity):
    """
    Records the nursing outcome of one scheduled medication dose.
    """

    __tablename__ = "medication_administrations"

    __table_args__ = (
        Index(
            "ix_medication_administrations_status",
            "status",
        ),
    )

    dose_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "medication_doses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    administered_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[MedicationAdministrationStatus] = mapped_column(
        SqlEnum(
            MedicationAdministrationStatus,
            name="medication_administration_status_enum",
        ),
        nullable=False,
    )

    administered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    dose_given: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dose: Mapped["MedicationDose"] = relationship(
        back_populates="administration",
    )

    administering_staff: Mapped["Staff"] = relationship(
        foreign_keys=[administered_by],
    )
