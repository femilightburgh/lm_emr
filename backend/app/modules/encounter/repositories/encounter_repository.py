"""
LIGHTBURGH EMR

Encounter Repository

==============================================================================

Provides data access operations for Encounters.

Business rules belong in EncounterService.

Hospital ownership is inherited through the Encounter's Episode.

==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.encounter.models import Encounter
from app.modules.episode.models import Episode


class EncounterRepository:
    """
    Repository for Encounter persistence.
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
        encounter: Encounter,
    ) -> Encounter:
        """
        Persist a new Encounter.
        """

        self.db.add(encounter)

        return encounter

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        encounter_id: UUID,
    ) -> Encounter | None:
        """
        Retrieve an Encounter by ID within the authenticated Hospital.

        Hospital ownership is enforced through the Encounter's Episode.
        """

        statement = (
            select(Encounter)
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                Encounter.id == encounter_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # Episode Encounters
    # ------------------------------------------------------------------

    def list_by_episode(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> list[Encounter]:
        """
        Return all Encounters belonging to an Episode
        within the authenticated Hospital.
        """

        statement = (
            select(Encounter)
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                Encounter.episode_id == episode_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                Encounter.started_at.asc(),
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
        encounter: Encounter,
    ) -> None:
        """
        Refresh an Encounter from the database.
        """

        self.db.refresh(encounter)