"""
==============================================================================
LIGHTBURGH EMR

Reception Patient Flow Schemas
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.episode.models import (
    EpisodeFlowStatus,
    EpisodeStatus,
)


class ReceptionPatientFlowItem(BaseModel):
    """
    Patient flow information visible to Reception.
    """

    id: UUID
    patient_id: UUID
    patient_name: str
    hospital_number: str

    episode_number: str
    title: str

    status: EpisodeStatus
    flow_status: EpisodeFlowStatus

    professional_name: str | None
    professional_role: str | None
    department_name: str | None

    checked_in_at: datetime | None
    opened_at: datetime


class ReceptionPatientFlowResponse(BaseModel):
    """
    Active patient-flow records visible to Reception.
    """

    items: list[ReceptionPatientFlowItem]
