"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Model
==============================================================================

A Clinical Order represents a request for work to be performed for a patient.

Hierarchy:

    Clinical Order
        -> Encounter
            -> Episode
                -> Hospital
==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.clinical_orders.enums import (
    ClinicalOrderStatus,
    ClinicalOrderType,
)

if TYPE_CHECKING:
    from app.modules.encounter.models import Encounter
    from app.modules.staff.models import Staff


class ClinicalOrder(BaseEntity):
    """
    Represents a clinical request created during an Encounter.
    """

    __tablename__ = "clinical_orders"

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------

    encounter_id: Mapped[UUID] = mapped_column(
        ForeignKey("encounters.id"),
        nullable=False,
        index=True,
    )

    ordered_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Order Information
    # ------------------------------------------------------------------

    order_type: Mapped[ClinicalOrderType] = mapped_column(
        SqlEnum(
            ClinicalOrderType,
            name="clinical_order_type_enum",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[ClinicalOrderStatus] = mapped_column(
        SqlEnum(
            ClinicalOrderStatus,
            name="clinical_order_status_enum",
        ),
        nullable=False,
        default=ClinicalOrderStatus.REQUESTED,
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        nullable=False,
        default="ROUTINE",
        index=True,
    )

    # ------------------------------------------------------------------
    # Clinical Request
    # ------------------------------------------------------------------

    details: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    encounter: Mapped["Encounter"] = relationship()

    prescription: Mapped["Prescription | None"] = relationship(
        back_populates="clinical_order",
        uselist=False,
    )

    ordering_staff: Mapped["Staff"] = relationship(
        foreign_keys=[ordered_by],
    )
