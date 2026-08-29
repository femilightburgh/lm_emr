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


class CreatePrescriptionRequest(BaseModel):
    """
    Structured medication prescription payload.
    """

    encounter_id: UUID = Field(
        ...,
        description="Encounter in which the prescription is issued.",
    )

    priority: str = Field(
        default="ROUTINE",
        min_length=1,
        max_length=50,
    )

    medicine_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    strength: str | None = Field(
        default=None,
        max_length=100,
    )

    dose: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    dose_unit: str | None = Field(
        default=None,
        max_length=50,
    )

    route: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    frequency: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    duration: str | None = Field(
        default=None,
        max_length=100,
    )

    duration_unit: str | None = Field(
        default=None,
        max_length=50,
    )

    quantity: str | None = Field(
        default=None,
        max_length=100,
    )

    directions: str | None = None

    indication: str | None = None
