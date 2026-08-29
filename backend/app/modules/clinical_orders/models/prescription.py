"""
==============================================================================
LIGHTBURGH EMR

Prescription Model
==============================================================================
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.modules.clinical_orders.models.clinical_order import (
        ClinicalOrder,
    )


class Prescription(BaseEntity):
    """
    Structured medication prescription belonging to a Medication ClinicalOrder.
    """

    __tablename__ = "prescriptions"

    clinical_order_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinical_orders.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    medicine_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    strength: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    dose: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    dose_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    route: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    frequency: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    duration: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    duration_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    quantity: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    directions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    indication: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    clinical_order: Mapped["ClinicalOrder"] = relationship(
        back_populates="prescription",
    )
