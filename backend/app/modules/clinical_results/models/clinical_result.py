"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Model
==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    String,
    Text,
    Enum as SqlEnum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.clinical_results.enums import (
    ClinicalResultStatus,
    ClinicalResultType,
)

if TYPE_CHECKING:
    from app.modules.clinical_orders.models import (
        ClinicalOrder,
        ClinicalOrderItem,
    )
    from app.modules.staff.models import Staff


class ClinicalResult(BaseEntity):
    """
    A result recorded against a Clinical Order.
    """

    __tablename__ = "clinical_results"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinical_orders.id"),
        nullable=False,
        index=True,
    )

    order_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinical_order_items.id"),
        nullable=True,
        index=True,
    )

    result_type: Mapped[ClinicalResultType] = mapped_column(
        SqlEnum(
            ClinicalResultType,
            name="clinical_result_type_enum",
        ),
        nullable=False,
        index=True,
    )

    
    status: Mapped[ClinicalResultStatus] = mapped_column(
        SqlEnum(
            ClinicalResultStatus,
            name="clinical_result_status_enum",
        ),
        nullable=False,
        default=ClinicalResultStatus.FINAL,
        index=True,
    )

    result_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    specimen: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    collected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    reported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    interpretation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recorded_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    order: Mapped["ClinicalOrder"] = relationship()

    order_item: Mapped["ClinicalOrderItem"] = relationship()

    recording_staff: Mapped["Staff"] = relationship(
        foreign_keys=[recorded_by],
    )

    values = relationship(
        "ClinicalResultValue",
        back_populates="clinical_result",
        cascade="all, delete-orphan",
        order_by="ClinicalResultValue.created_at",
    )
