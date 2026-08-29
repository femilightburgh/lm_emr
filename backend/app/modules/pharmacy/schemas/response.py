"""
==============================================================================
LIGHTBURGH EMR

Pharmacy Response Schemas
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


class PharmacyQueueItemResponse(BaseModel):
    """
    Medication order requiring pharmacy attention.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    encounter_id: UUID
    patient_id: UUID
    patient_name: str
    hospital_number: str
    episode_number: str
    ordering_clinician_name: str

    order_type: ClinicalOrderType
    status: ClinicalOrderStatus
    priority: str
    details: dict[str, Any]

    prescription_id: UUID | None
    medicine_name: str | None
    strength: str | None
    dose: str | None
    dose_unit: str | None
    route: str | None
    frequency: str | None
    duration: str | None
    duration_unit: str | None
    quantity: str | None
    directions: str | None
    indication: str | None

    ordered_at: datetime
    started_at: datetime | None


class DispensePrescriptionResponse(BaseModel):
    """
    Result of a successful prescription dispensing action.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    prescription_id: UUID
    dispensed_by: UUID
    quantity_dispensed: str
    dispensed_at: datetime
    notes: str | None
