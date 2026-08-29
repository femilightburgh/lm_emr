"""
==============================================================================
LIGHTBURGH EMR

Episode Repository

==============================================================================

Provides persistence operations for Episodes of Care.

Business rules belong in EpisodeService.

Hospital tenancy is enforced by repository query predicates.
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.episode.models import (
    Episode,
    EpisodeFlowStatus,
    EpisodeStatus,
)

from app.modules.patients.models import Patient


class EpisodeRepository:
    """
    Repository for Episode persistence.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # =========================================================================
    # Create
    # =========================================================================

    def create(
        self,
        *,
        episode: Episode,
    ) -> Episode:
        """
        Add an Episode to the current transaction.
        """

        self.db.add(episode)

        return episode

    # =========================================================================
    # Retrieve
    # =========================================================================

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> Episode | None:
        """
        Retrieve an Episode by ID within a Hospital.
        """

        statement = (
            select(Episode)
            .where(
                Episode.id == episode_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # =========================================================================
    # Episode Number
    # =========================================================================

    def get_by_episode_number(
        self,
        *,
        hospital_id: UUID,
        episode_number: str,
    ) -> Episode | None:
        """
        Retrieve an Episode by hospital-scoped episode number.
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
        Retrieve the latest Episode number assigned to a Hospital.
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

    # =========================================================================
    # Nursing Queue
    # =========================================================================

    def list_nursing_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[Episode]:
        """
        Return Episodes currently requiring nursing attention.

        Includes:

            WAITING_FOR_NURSING
            NURSING_IN_PROGRESS

        Results are ordered by check-in time so the oldest patient
        appears first.
        """

        statement = (
            select(Episode)
            .where(
                Episode.hospital_id == hospital_id,
                Episode.flow_status.in_(
                    (
                        EpisodeFlowStatus.WAITING_FOR_NURSING,
                        EpisodeFlowStatus.NURSING_IN_PROGRESS,
                    ),
                ),
            )
            .order_by(
                Episode.checked_in_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Doctor Clinic Queue
    # =========================================================================

    def list_doctor_clinic_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[Episode]:
        """
        Return open Episodes routed to the Doctor workflow.
        """

        statement = (
            select(Episode)
            .join(
                Patient,
                Patient.id == Episode.patient_id,
            )
            .where(
                Episode.hospital_id == hospital_id,
                Episode.status == EpisodeStatus.OPEN,
                Episode.flow_status.in_(
                    (
                        EpisodeFlowStatus.ROUTED,
                        EpisodeFlowStatus.AWAITING_REVIEW,
                    ),
                ),
            )
            .order_by(
                Episode.routed_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Doctor Ward Queue
    # =========================================================================

    def list_doctor_ward_queue(
        self,
        *,
        hospital_id: UUID,
        managing_doctor_id: UUID,
    ) -> list[Episode]:
        """
        Return admitted Episodes managed by the authenticated Doctor.
        """

        statement = (
            select(Episode)
            .join(
                Patient,
                Patient.id == Episode.patient_id,
            )
            .where(
                Episode.hospital_id == hospital_id,
                Episode.status == EpisodeStatus.ADMITTED,
                Episode.managing_doctor_id == managing_doctor_id,
            )
            .order_by(
                Episode.routed_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Patient Episodes
    # =========================================================================

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

    # =========================================================================
    # Persistence
    # =========================================================================

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

    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """

        self.db.rollback()