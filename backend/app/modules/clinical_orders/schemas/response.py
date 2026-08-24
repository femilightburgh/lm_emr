"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Response Schemas
==============================================================================
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.clinical_orders.enums import (
    ClinicalOrderStatus,
    ClinicalOrderType,
)


class ClinicalOrderResponse(BaseModel):
    """
    Clinical Order response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    encounter_id: UUID

    ordered_by: UUID

    order_type: ClinicalOrderType

    status: ClinicalOrderStatus

    priority: str

    details: dict[str, Any]

    ordered_at: datetime

    started_at: datetime | None

    completed_at: datetime | None

    cancelled_at: datetime | None

    created_at: datetime

    updated_at: datetime
