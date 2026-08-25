from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.diagnoses.enums import (
    DiagnosisCertainty,
    DiagnosisType,
)


class CreateClinicalDiagnosisRequest(BaseModel):
    """
    Request to record a clinical diagnosis.
    """

    encounter_id: UUID = Field(
        ...,
        description="Encounter in which the diagnosis is recorded.",
    )

    diagnosis_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Clinical diagnosis display name.",
    )

    code_system: str | None = Field(
        default=None,
        max_length=50,
        description="Terminology or coding system, e.g. ICD-10-CM.",
    )

    code: str | None = Field(
        default=None,
        max_length=50,
        description="Code within the specified terminology system.",
    )

    diagnosis_type: DiagnosisType = Field(
        ...,
        description="Clinical role of the diagnosis.",
    )

    certainty: DiagnosisCertainty = Field(
        ...,
        description="Clinician's certainty about the diagnosis.",
    )

    onset_date: date | None = Field(
        default=None,
        description="Date the condition is believed to have started.",
    )

    notes: str | None = Field(
        default=None,
        description="Additional clinical context.",
    )
