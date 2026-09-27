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
from app.modules.clinical_orders.models import ClinicalOrderItemType


class PrescriptionResponse(BaseModel):
    """
    Structured medication prescription response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    clinical_order_id: UUID
    medicine_name: str
    strength: str | None
    dose: str
    dose_unit: str | None
    route: str
    frequency: str
    duration: str | None
    duration_unit: str | None
    quantity: str | None
    directions: str | None
    indication: str | None
    created_at: datetime
    updated_at: datetime


class ClinicalOrderItemResponse(BaseModel):
    """
    Investigation item contained within a Clinical Order.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    clinical_order_id: UUID

    item_type: ClinicalOrderItemType

    status: ClinicalOrderStatus

    laboratory_test_id: UUID | None

    diagnostic_investigation_id: UUID | None

    custom_name: str | None

    display_order: int

    details: dict[str, Any]

    created_at: datetime

    updated_at: datetime


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

    items: list[ClinicalOrderItemResponse]

    ordered_at: datetime

    started_at: datetime | None

    completed_at: datetime | None

    cancelled_at: datetime | None

    created_at: datetime

    updated_at: datetime


class LaboratoryQueueItemResponse(BaseModel):
    """
    Clinical Order worklist item for Laboratory staff.
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

    items: list[ClinicalOrderItemResponse]

    ordered_at: datetime

    started_at: datetime | None


class DiagnosticQueueItemResponse(BaseModel):
    """
    Clinical Order worklist item for Diagnostics staff.
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
    items: list[ClinicalOrderItemResponse]
    ordered_at: datetime
    started_at: datetime | None
