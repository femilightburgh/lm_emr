"""
==============================================================================
LIGHTBURGH EMR

Episode Response Schemas
==============================================================================

Response DTOs for Episode operations.

==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.episode.models import (
    EpisodeFlowStatus,
    EpisodeStatus,
)


class DoctorQueueItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    patient_id: UUID
    patient_name: str
    hospital_number: str
    episode_number: str
    title: str
    status: EpisodeStatus
    flow_status: EpisodeFlowStatus
    managing_doctor_id: UUID | None
    checked_in_at: datetime | None
    routed_at: datetime | None


class EpisodeResponse(BaseModel):
    """
    Episode response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    hospital_id: UUID

    patient_id: UUID

    managing_doctor_id: UUID | None

    episode_number: str

    title: str

    # ------------------------------------------------------------------
    # Clinical lifecycle
    # ------------------------------------------------------------------

    status: EpisodeStatus

    # ------------------------------------------------------------------
    # Operational workflow
    # ------------------------------------------------------------------

    flow_status: EpisodeFlowStatus

    checked_in_at: datetime | None

    checked_in_by: UUID | None

    triaged_at: datetime | None

    triaged_by: UUID | None

    routed_at: datetime | None

    routed_by: UUID | None

    current_department_id: UUID | None

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    opened_at: datetime

    closed_at: datetime | None