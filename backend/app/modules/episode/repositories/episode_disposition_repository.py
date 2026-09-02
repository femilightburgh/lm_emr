"""
==============================================================================
LIGHTBURGH EMR

Episode Disposition Repository

==============================================================================

Purpose
-------
Provides persistence operations for Episode Disposition records.

Business rules belong in EpisodeService.
HTTP concerns belong in the API router.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.episode.models import EpisodeDisposition


class EpisodeDispositionRepository:
    """
    Persistence operations for Episode Dispositions.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        *,
        disposition: EpisodeDisposition,
    ) -> EpisodeDisposition:
        """
        Add a disposition to the current transaction.
        """

        self.db.add(disposition)

        return disposition

    def list_by_episode(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> list[EpisodeDisposition]:
        """
        Return dispositions belonging to an Episode.
        """

        statement = (
            select(EpisodeDisposition)
            .where(
                EpisodeDisposition.hospital_id == hospital_id,
                EpisodeDisposition.episode_id == episode_id,
            )
            .order_by(
                EpisodeDisposition.decided_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )
