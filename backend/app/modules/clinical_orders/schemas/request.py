"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Request Schemas
==============================================================================
"""

from uuid import UUID
from typing import Any

from pydantic import BaseModel, Field

from app.modules.clinical_orders.enums import ClinicalOrderType


class CreateClinicalOrderRequest(BaseModel):
    """
    Request to create a Clinical Order.
    """

    encounter_id: UUID = Field(
        ...,
        description="Encounter in which the order is placed.",
    )

    order_type: ClinicalOrderType = Field(
        ...,
        description="Type of Clinical Order.",
    )

    priority: str = Field(
        default="ROUTINE",
        min_length=1,
        max_length=50,
        description="Clinical priority of the order.",
    )

    details: dict[str, Any] = Field(
        ...,
        description="Type-specific order details.",
    )
