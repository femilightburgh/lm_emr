from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.diagnoses.enums import (
    DiagnosisCertainty,
    DiagnosisType,
)


class ClinicalDiagnosisResponse(BaseModel):
    """
    Clinical Diagnosis response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    encounter_id: UUID

    episode_id: UUID

    diagnosis_name: str

    code_system: str | None

    code: str | None

    diagnosis_type: DiagnosisType

    certainty: DiagnosisCertainty

    onset_date: date | None

    diagnosed_by: UUID

    diagnosed_at: datetime

    resolved_at: datetime | None

    notes: str | None

    created_at: datetime

    updated_at: datetime
