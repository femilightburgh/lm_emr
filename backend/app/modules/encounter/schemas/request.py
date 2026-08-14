"""
LIGHTBURGH EMR

Encounter Request Schemas

==============================================================================

Defines request payloads used by the Encounter API.

==============================================================================

"""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateEncounterRequest(BaseModel):
    """
    Request payload for starting a new professional Encounter.
    """

    episode_id: UUID = Field(
        ...,
        description="Identifier of the Episode of Care associated with the Encounter.",
    )

    staff_id: UUID = Field(
        ...,
        description="Identifier of the Staff member performing the Encounter.",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Purpose or nature of the professional attendance.",
    )