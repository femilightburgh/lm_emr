"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Response Schemas
==============================================================================
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.clinical_results.enums import (
    ClinicalResultStatus,
    ClinicalResultType,
)


class ClinicalResultValueResponse(BaseModel):
    """
    Self-describing structured result value.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    clinical_result_id: UUID

    analyte_id: UUID | None
    analyte_code: str | None
    analyte_name: str

    custom_analyte_name: str | None
    custom_analyte_code: str | None
    custom_unit: str | None
    custom_reference_low: float | None
    custom_reference_high: float | None
    custom_reference_text: str | None

    value: float | str | bool | None

    unit: str | None

    reference_low: float | None
    reference_high: float | None
    reference_text: str | None

    abnormal_flag: str | None
    comment: str | None

    created_at: datetime
    updated_at: datetime


class ClinicalResultResponse(BaseModel):
    """
    Clinical Result response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    order_id: UUID
    order_item_id: UUID | None
    result_type: ClinicalResultType
    status: ClinicalResultStatus

    specimen: str | None
    collected_at: datetime | None
    reported_at: datetime | None
    interpretation: str | None

    values: list[ClinicalResultValueResponse]

    # Temporary compatibility field.
    result_data: dict[str, Any]

    recorded_by: UUID
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime
