"""
==============================================================================
LIGHTBURGH EMR

Vitals Response Schemas
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.events.enums import EventType


class VitalsResponse(BaseModel):
    """
    Response returned after recording patient vital signs.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    encounter_id: UUID

    event_type: EventType

    performed_by: UUID

    occurred_at: datetime

    payload: dict