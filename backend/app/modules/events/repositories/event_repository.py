"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Repository

==============================================================================

Provides data access operations for Clinical Events.

Business rules belong in ClinicalEventService.

Hospital ownership is inherited through the Event's Encounter and Episode.

==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.encounter.models import Encounter
from app.modules.episode.models import Episode
from app.modules.events.models import ClinicalEvent


class ClinicalEventRepository:
    """
    Repository for Clinical Event persistence.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        event: ClinicalEvent,
    ) -> ClinicalEvent:
        """
        Persist a new Clinical Event.
        """

        self.db.add(event)

        return event

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        event_id: UUID,
    ) -> ClinicalEvent | None:
        """
        Retrieve a Clinical Event by ID within the authenticated Hospital.

        Hospital ownership is enforced through the Event's Encounter
        and Episode.
        """

        statement = (
            select(ClinicalEvent)
            .join(
                Encounter,
                ClinicalEvent.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalEvent.id == event_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # Encounter Events
    # ------------------------------------------------------------------

    def list_by_encounter(
        self,
        *,
        hospital_id: UUID,
        encounter_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all Clinical Events belonging to an Encounter
        within the authenticated Hospital.
        """

        statement = (
            select(ClinicalEvent)
            .join(
                Encounter,
                ClinicalEvent.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalEvent.encounter_id == encounter_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalEvent.occurred_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Episode Events
    # ------------------------------------------------------------------

    def list_by_episode(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all Clinical Events belonging to an Episode
        within the authenticated Hospital.

        Events are returned in clinical occurrence order.
        """

        statement = (
            select(ClinicalEvent)
            .join(
                Encounter,
                ClinicalEvent.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                Encounter.episode_id == episode_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalEvent.occurred_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """
        Commit the current transaction.
        """

        self.db.commit()

    def refresh(
        self,
        event: ClinicalEvent,
    ) -> None:
        """
        Refresh a Clinical Event from the database.
        """

        self.db.refresh(event)