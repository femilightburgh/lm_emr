"""
==============================================================================
LIGHTBURGH EMR

Medication Dispensing Model
==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.modules.clinical_orders.models import Prescription
    from app.modules.staff.models import Staff


class Dispensing(BaseEntity):
    """
    Records a pharmacy dispensing action for a Prescription.

    The first pharmacy implementation permits one dispensing record
    per prescription. Partial/multiple dispensing can be introduced
    later without changing the prescription itself.
    """

    __tablename__ = "dispensings"

    prescription_id: Mapped[UUID] = mapped_column(
        ForeignKey("prescriptions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    dispensed_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    quantity_dispensed: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    dispensed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    prescription: Mapped["Prescription"] = relationship()

    dispensing_staff: Mapped["Staff"] = relationship(
        foreign_keys=[dispensed_by],
    )
