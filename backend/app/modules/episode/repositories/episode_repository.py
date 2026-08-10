"""
==============================================================================
LIGHTBURGH EMR

Episode Repository

==============================================================================

Purpose
-------

Provides data access operations for Episodes of Care.

Business rules belong in EpisodeService.

This repository is responsible only for persistence.

==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.episode.models import Episode


class EpisodeRepository:
    """
    Repository for Episode persistence.
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
        episode: Episode,
    ) -> Episode:
        """
        Persist a new Episode.
        """

        self.db.add(episode)

        return episode

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> Episode | None:
        """
        Retrieve an Episode by its primary key.

        The primary key lookup is performed using SQLAlchemy's
        Session.get() identity lookup. The returned Episode is then
        verified against the authenticated Hospital to preserve
        tenant isolation.
        """

        episode = self.db.get(
            Episode,
            episode_id,
        )

        if episode is None:
            return None

        if episode.hospital_id != hospital_id:
            return None

        return episode

    # ------------------------------------------------------------------
    # Episode Number
    # ------------------------------------------------------------------

    def get_by_episode_number(
        self,
        *,
        hospital_id: UUID,
        episode_number: str,
    ) -> Episode | None:
        """
        Retrieve an Episode by its hospital-scoped episode number.
        """

        statement = (
            select(Episode)
            .where(
                Episode.hospital_id == hospital_id,
                Episode.episode_number == episode_number,
            )
        )

        return self.db.scalar(statement)

    def get_latest_episode_number(
        self,
        *,
        hospital_id: UUID,
    ) -> str | None:
        """
        Retrieve the most recently assigned Episode number
        for a specific hospital.
        """

        statement = (
            select(Episode.episode_number)
            .where(
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                Episode.episode_number.desc(),
            )
            .limit(1)
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # Patient Episodes
    # ------------------------------------------------------------------

    def list_by_patient(
        self,
        *,
        hospital_id: UUID,
        patient_id: UUID,
    ) -> list[Episode]:
        """
        Return all Episodes belonging to a Patient
        within the authenticated Hospital.
        """

        statement = (
            select(Episode)
            .where(
                Episode.hospital_id == hospital_id,
                Episode.patient_id == patient_id,
            )
            .order_by(
                Episode.opened_at.desc(),
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
        episode: Episode,
    ) -> None:
        """
        Refresh an Episode from the database.
        """

        self.db.refresh(episode)