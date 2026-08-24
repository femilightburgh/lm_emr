"""
==============================================================================
LIGHTBURGH EMR

Vitals Request Schemas
==============================================================================

Defines API request payloads for recording clinical vital signs.

Vitals are persisted as a ClinicalEvent with:

    event_type = VITALS_RECORDED

The schema deliberately validates the structure of the clinical data
before it reaches the ClinicalEventService.
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class CreateVitalsRequest(BaseModel):
    """
    Request to record a set of patient vital signs.

    At least one vital sign must be provided.
    """

    encounter_id: UUID = Field(
        ...,
        description="Encounter in which the vital signs were recorded.",
    )

    occurred_at: datetime = Field(
        ...,
        description="Time at which the vital signs were actually obtained.",
    )

    temperature: float | None = Field(
        default=None,
        ge=20.0,
        le=45.0,
        description="Body temperature in degrees Celsius.",
    )

    heart_rate: int | None = Field(
        default=None,
        ge=20,
        le=300,
        description="Heart rate in beats per minute.",
    )

    respiratory_rate: int | None = Field(
        default=None,
        ge=5,
        le=100,
        description="Respiratory rate in breaths per minute.",
    )

    systolic_bp: int | None = Field(
        default=None,
        ge=40,
        le=300,
        description="Systolic blood pressure in mmHg.",
    )

    diastolic_bp: int | None = Field(
        default=None,
        ge=20,
        le=200,
        description="Diastolic blood pressure in mmHg.",
    )

    spo2: int | None = Field(
        default=None,
        ge=50,
        le=100,
        description="Peripheral oxygen saturation as a percentage.",
    )

    weight: float | None = Field(
        default=None,
        ge=0.1,
        le=500.0,
        description="Body weight in kilograms.",
    )

    @model_validator(mode="after")
    def require_at_least_one_vital(self):
        """
        At least one clinical measurement must be provided.
        """

        measurements = (
            self.temperature,
            self.heart_rate,
            self.respiratory_rate,
            self.systolic_bp,
            self.diastolic_bp,
            self.spo2,
            self.weight,
        )

        if all(value is None for value in measurements):
            raise ValueError(
                "At least one vital sign must be provided.",
            )

        return self