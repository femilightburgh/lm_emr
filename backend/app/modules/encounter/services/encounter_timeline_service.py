"""
==============================================================================
LIGHTBURGH EMR

Encounter Timeline Service
==============================================================================

Provides the read-side business logic for the clinical timeline of an
Encounter.

The timeline is not a separate database entity.

Clinical Events remain the source of truth:

    Encounter
        ↓
    Clinical Events
        ↓
    Timeline

Hospital tenancy is enforced through the Encounter and Clinical Event
repositories.
==============================================================================
"""

from uuid import UUID

from app.core.context import RequestContext
from app.modules.encounter.exceptions import EncounterNotFoundError
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.events.models import ClinicalEvent
from app.modules.events.repositories import ClinicalEventRepository


class EncounterTimelineService:
    """
    Service responsible for retrieving the clinical timeline of an Encounter.
    """

    def __init__(
        self,
        *,
        encounter_repository: EncounterRepository,
        event_repository: ClinicalEventRepository,
    ) -> None:
        self.encounter_repository = encounter_repository
        self.event_repository = event_repository

    # ------------------------------------------------------------------
    # Encounter Timeline
    # ------------------------------------------------------------------

    def get_timeline(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all Clinical Events belonging to an Encounter.

        The Encounter must belong to the authenticated Hospital.

        Events are returned in clinical occurrence order.
        """

        # --------------------------------------------------------------
        # Verify Encounter ownership
        # --------------------------------------------------------------

        encounter = self.encounter_repository.get_by_id(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError(
                "Encounter not found.",
            )

        # --------------------------------------------------------------
        # Retrieve Clinical Events
        # --------------------------------------------------------------

        return self.event_repository.list_by_encounter(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )