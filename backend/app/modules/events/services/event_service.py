"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Service
==============================================================================

Business logic for Clinical Events.

A Clinical Event:
    • belongs to an Encounter
    • is performed by a Staff member
    • records what happened
    • records when it happened
    • stores event-specific clinical data in payload

Hospital tenancy is enforced through:

    Event → Encounter → Episode → Hospital

The performer must also belong to the current Hospital.
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.exceptions import (
    EncounterNotFoundError,
    EventNotFoundError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.events.models import ClinicalEvent
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.staff.repository import StaffRepository


class ClinicalEventService:
    """
    Service responsible for Clinical Event business logic.
    """

    def __init__(
        self,
        *,
        repository: ClinicalEventRepository,
    ) -> None:
        self.repository = repository

        self.encounter_repository = EncounterRepository(
            repository.db,
        )

        self.staff_repository = StaffRepository(
            repository.db,
        )

    # ------------------------------------------------------------------
    # Create Event
    # ------------------------------------------------------------------

    def create_event(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
        event_type: EventType,
        performed_by: UUID,
        occurred_at: datetime,
        payload: dict | None = None,
        commit: bool = True,
    ) -> ClinicalEvent:
        """
        Create a Clinical Event within the current Hospital.

        By default, the event is committed immediately.

        Higher-level services that need multiple database operations to
        succeed atomically may pass commit=False and commit the transaction
        themselves.
        """

        # ------------------------------------------------------------------
        # Validate Event Type
        # ------------------------------------------------------------------

        if not isinstance(event_type, EventType):
            raise ValueError(
                "Invalid clinical event type.",
            )

        # ------------------------------------------------------------------
        # Encounter
        # ------------------------------------------------------------------

        encounter = self.encounter_repository.get_by_id(
            encounter_id=encounter_id,
            hospital_id=context.hospital_id,
        )

        if encounter is None:
            raise EncounterNotFoundError(
                "Encounter not found.",
            )

        # ------------------------------------------------------------------
        # Performer
        # ------------------------------------------------------------------

        staff = self.staff_repository.get_by_id(
            performed_by,
        )

        if staff is None:
            raise StaffNotFoundError(
                "Staff member not found.",
            )

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError(
                "Staff member belongs to another hospital.",
            )

        # ------------------------------------------------------------------
        # Create Event
        # ------------------------------------------------------------------

        event = ClinicalEvent(
            encounter_id=encounter.id,
            event_type=event_type,
            performed_by=staff.id,
            occurred_at=occurred_at,
            payload=payload,
        )

        self.repository.create(
            event=event,
        )

        # ------------------------------------------------------------------
        # Transaction Handling
        # ------------------------------------------------------------------

        if commit:
            self.repository.save()
        else:
            # Flush so the event is actually sent to PostgreSQL and receives
            # its generated values without committing the transaction.
            self.repository.db.flush()

        self.repository.refresh(event)

        return event

    # ------------------------------------------------------------------
    # Retrieve Event
    # ------------------------------------------------------------------

    def get_event(
        self,
        *,
        context: RequestContext,
        event_id: UUID,
    ) -> ClinicalEvent:
        """
        Retrieve a Clinical Event belonging to the current Hospital.
        """

        event = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            event_id=event_id,
        )

        if event is None:
            raise EventNotFoundError(
                "Clinical Event not found.",
            )

        return event

    # ------------------------------------------------------------------
    # List Encounter Events
    # ------------------------------------------------------------------

    def list_encounter_events(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all Clinical Events belonging to an Encounter
        within the authenticated Hospital.

        Events are returned in clinical occurrence order.

        Hospital tenancy is enforced by the repository.
        """

        return self.repository.list_by_encounter(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

    # ------------------------------------------------------------------
    # List Episode Events
    # ------------------------------------------------------------------

    def list_episode_events(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all Clinical Events belonging to an Episode
        within the authenticated Hospital.

        Events are returned in clinical occurrence order.
        Hospital tenancy is enforced by the repository.
        """

        return self.repository.list_by_episode(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )
