"""
LIGHTBURGH EMR

Encounter Response Schemas

==============================================================================

Defines response DTOs returned by the Encounter API.

==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.encounter.models import EncounterStatus


class EncounterResponse(BaseModel):
    """
    Encounter response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    episode_id: UUID

    staff_id: UUID

    title: str

    status: EncounterStatus

    started_at: datetime

    ended_at: datetime | None