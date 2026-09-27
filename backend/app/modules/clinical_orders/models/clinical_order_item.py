"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Item Model
==============================================================================

A ClinicalOrderItem represents one investigation within a ClinicalOrder.

Hierarchy:

    ClinicalOrder
        -> ClinicalOrderItem
            -> LaboratoryTest
            -> DiagnosticInvestigation

A ClinicalOrder may contain multiple investigation items while remaining
one patient request.
==============================================================================
"""

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum as SqlEnum,
    ForeignKey,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.clinical_orders.enums import ClinicalOrderStatus

if TYPE_CHECKING:
    from app.modules.clinical_orders.models.clinical_order import ClinicalOrder
    from app.modules.diagnostics.models import DiagnosticInvestigation
    from app.modules.laboratory.models import LaboratoryTest


class ClinicalOrderItemType(str, Enum):
    """
    Catalogue type represented by a ClinicalOrderItem.
    """

    LABORATORY = "LABORATORY"
    DIAGNOSTIC = "DIAGNOSTIC"


class ClinicalOrderItem(BaseEntity):
    """
    One investigation requested within a ClinicalOrder.
    """

    __tablename__ = "clinical_order_items"

    __table_args__ = (
        UniqueConstraint(
            "clinical_order_id",
            "laboratory_test_id",
            name="uq_clinical_order_item_laboratory_test",
        ),
        UniqueConstraint(
            "clinical_order_id",
            "diagnostic_investigation_id",
            name="uq_clinical_order_item_diagnostic_investigation",
        ),
    )

    clinical_order_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinical_orders.id"),
        nullable=False,
        index=True,
    )

    item_type: Mapped[ClinicalOrderItemType] = mapped_column(
        SqlEnum(
            ClinicalOrderItemType,
            name="clinical_order_item_type_enum",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[ClinicalOrderStatus] = mapped_column(
        SqlEnum(
            ClinicalOrderStatus,
            name="clinical_order_item_status_enum",
        ),
        nullable=False,
        default=ClinicalOrderStatus.REQUESTED,
        index=True,
    )

    laboratory_test_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("laboratory_tests.id"),
        nullable=True,
        index=True,
    )

    diagnostic_investigation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("diagnostic_investigations.id"),
        nullable=True,
        index=True,
    )

    custom_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    details: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    clinical_order: Mapped["ClinicalOrder"] = relationship(
        back_populates="items",
    )

    laboratory_test: Mapped["LaboratoryTest | None"] = relationship()

    diagnostic_investigation: Mapped[
        "DiagnosticInvestigation | None"
    ] = relationship()
