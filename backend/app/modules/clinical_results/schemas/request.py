"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Request Schemas
==============================================================================
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.clinical_results.enums import (
    ClinicalResultStatus,
    ClinicalResultType,
)


class ClinicalResultValueRequest(BaseModel):
    """
    One analyte value within a laboratory result.
    """

    analyte_id: UUID = Field(
        ...,
        description="Laboratory analyte being reported.",
    )

    value_numeric: float | None = None
    value_text: str | None = None
    value_boolean: bool | None = None
    value_code: str | None = None

    abnormal_flag: str | None = Field(
        default=None,
        max_length=50,
    )

    comment: str | None = None


class CreateClinicalResultRequest(BaseModel):
    """
    Record a result against a Clinical Order.

    `values` is the canonical structured laboratory result payload.
    `result_data` remains temporarily supported for backward compatibility.
    """

    order_id: UUID = Field(
        ...,
        description="Parent Clinical Order for the result.",
    )

    order_item_id: UUID | None = Field(
        default=None,
        description="Specific Clinical Order Item for the result.",
    )

    result_type: ClinicalResultType = Field(
        ...,
        description="Type of result being recorded.",
    )

    status: ClinicalResultStatus = Field(
        default=ClinicalResultStatus.FINAL,
        description="Whether the result is a draft or finalized report.",
    )

    specimen: str | None = None
    collected_at: datetime | None = None
    reported_at: datetime | None = None
    interpretation: str | None = None

    values: list[ClinicalResultValueRequest] = Field(
        default_factory=list,
        description="Structured laboratory analyte values.",
    )

    # Temporary compatibility path.
    result_data: dict[str, Any] | None = Field(
        default=None,
        description="Legacy result payload; retained during migration.",
    )
