"""
==============================================================================
LIGHTBURGH EMR

Episode Service

==============================================================================

Purpose
-------

Contains the business logic for managing Episodes of Care.

Responsibilities
----------------
• Create Episodes.
• Generate hospital-scoped Episode numbers.
• Retrieve Episodes.
• List Episodes belonging to a Patient.

Database access belongs in repositories.

HTTP concerns belong in routers.

==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.episode.exceptions import (
    EpisodeAlreadyExistsError,
    EpisodeNotFoundError,
    PatientNotFoundError,
)
from app.modules.episode.models import Episode, EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)


class EpisodeService:
    """
    Business logic for Episodes of Care.
    """

    def __init__(
        self,
        repository: EpisodeRepository,
        patient_repository: PatientRepository,
        number_generator: EpisodeNumberGenerator,
    ) -> None:
        self.repository = repository
        self.patient_repository = patient_repository
        self.number_generator = number_generator

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_episode(
        self,
        *,
        context: RequestContext,
        patient_id: UUID,
        title: str,
    ) -> Episode:
        """
        Create a new Episode of Care.

        The Episode number is generated automatically from the
        authenticated hospital context.
        """

        patient = self.patient_repository.get_by_id(
            patient_id=patient_id,
        )

        if patient is None:
            raise PatientNotFoundError()

        # --------------------------------------------------------------
        # Verify Patient belongs to the authenticated Hospital
        # --------------------------------------------------------------

        if patient.hospital_id != context.hospital_id:
            raise PatientNotFoundError()

        # --------------------------------------------------------------
        # Generate Episode Number
        # --------------------------------------------------------------

        episode_number = self.number_generator.generate(
            hospital_id=context.hospital_id,
        )

        # --------------------------------------------------------------
        # Defensive duplicate check
        # --------------------------------------------------------------

        existing = self.repository.get_by_episode_number(
            hospital_id=context.hospital_id,
            episode_number=episode_number,
        )

        if existing is not None:
            raise EpisodeAlreadyExistsError()

        # --------------------------------------------------------------
        # Create Episode
        # --------------------------------------------------------------

        episode = Episode(
            hospital_id=context.hospital_id,
            patient_id=patient_id,
            episode_number=episode_number,
            title=title,
            status=EpisodeStatus.OPEN,
            opened_at=datetime.now(UTC),
            closed_at=None,
        )

        self.repository.create(
            episode=episode,
        )

        self.repository.save()
        self.repository.refresh(
            episode,
        )

        return episode

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> Episode:
        """
        Retrieve an Episode within the authenticated Hospital.
        """

        episode = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )

        if episode is None:
            raise EpisodeNotFoundError()

        return episode

    # ------------------------------------------------------------------
    # Patient Episodes
    # ------------------------------------------------------------------

    def list_patient_episodes(
        self,
        *,
        context: RequestContext,
        patient_id: UUID,
    ) -> list[Episode]:
        """
        Return all Episodes belonging to a Patient
        within the authenticated Hospital.
        """

        return self.repository.list_by_patient(
            hospital_id=context.hospital_id,
            patient_id=patient_id,
        )