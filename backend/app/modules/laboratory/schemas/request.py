"""
==============================================================================
LIGHTBURGH EMR

Laboratory Catalogue Request Schemas
==============================================================================
"""

from typing import Any

from pydantic import BaseModel, Field

from app.modules.laboratory.enums import (
    LaboratoryAnalyteDataType,
)


class CreateLaboratoryAnalyteRequest(BaseModel):
    """
    Create a structured analyte belonging to a laboratory test.
    """

    code: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    data_type: LaboratoryAnalyteDataType

    unit: str | None = Field(
        default=None,
        max_length=100,
    )

    reference_low: float | None = None

    reference_high: float | None = None

    reference_text: str | None = None

    options: list[Any] | None = None

    required: bool = False

    display_order: int = Field(
        default=0,
        ge=0,
    )


class CreateLaboratoryTestRequest(BaseModel):
    """
    Create a hospital laboratory investigation and its analytes.
    """

    code: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    specimen: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    analytes: list[
        CreateLaboratoryAnalyteRequest
    ] = Field(
        default_factory=list,
    )


class UpdateLaboratoryTestRequest(BaseModel):
    """
    Update laboratory investigation metadata.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    specimen: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    active: bool | None = None


class UpdateLaboratoryAnalyteRequest(BaseModel):
    """
    Update laboratory analyte catalogue metadata.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    unit: str | None = Field(
        default=None,
        max_length=100,
    )

    reference_low: float | None = None

    reference_high: float | None = None

    reference_text: str | None = None

    options: list[Any] | None = None

    required: bool | None = None

    display_order: int | None = Field(
        default=None,
        ge=0,
    )
