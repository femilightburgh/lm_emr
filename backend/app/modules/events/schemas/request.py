"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Request Schemas

==============================================================================

Defines request payloads used by the Clinical Event API.

==============================================================================
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.events.enums import EventType


class CreateClinicalEventRequest(BaseModel):
    """
    Request to record a Clinical Event.
    """

    encounter_id: UUID = Field(
        ...,
        description="Encounter in which the clinical action occurred.",
    )

    event_type: EventType = Field(
        ...,
        description="Type of clinical action being recorded.",
    )

    performed_by: UUID = Field(
        ...,
        description="Staff member who performed the clinical action.",
    )

    occurred_at: datetime = Field(
        ...,
        description="Date and time when the clinical action occurred.",
    )

    payload: dict[str, Any] | None = Field(
        default=None,
        description="Event-specific clinical data.",
    )