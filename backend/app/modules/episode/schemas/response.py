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

from app.modules.episode.models import EpisodeStatus


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

    status: EpisodeStatus

    opened_at: datetime

    closed_at: datetime | None