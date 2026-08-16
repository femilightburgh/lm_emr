"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Response Schemas

==============================================================================
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.events.enums import EventType


class ClinicalEventResponse(BaseModel):
    """
    Clinical Event response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    encounter_id: UUID

    event_type: EventType

    performed_by: UUID

    occurred_at: datetime

    payload: dict[str, Any] | None

    created_at: datetime

    updated_at: datetime
    