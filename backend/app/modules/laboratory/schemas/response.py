"""
==============================================================================
LIGHTBURGH EMR

Laboratory Test Response Schemas
==============================================================================
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.laboratory.enums import (
    LaboratoryAnalyteDataType,
)


class LaboratoryTestAnalyteResponse(BaseModel):
    """
    Structured analyte definition belonging to a laboratory test.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    laboratory_test_id: UUID
    code: str
    name: str
    data_type: LaboratoryAnalyteDataType
    unit: str | None
    reference_low: float | None
    reference_high: float | None
    reference_text: str | None
    options: list[Any] | None
    required: bool
    display_order: int


class LaboratoryTestResponse(BaseModel):
    """
    Laboratory Test catalogue response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    code: str
    name: str
    specimen: str | None
    description: str | None

    analytes: list[LaboratoryTestAnalyteResponse]

    active: bool
