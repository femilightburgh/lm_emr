"""
==============================================================================
LIGHTBURGH EMR

Encounter Service

==============================================================================

Contains the business logic for managing Encounters.

Database access belongs in EncounterRepository.

HTTP concerns belong in the API router.

An Encounter may be created while its Episode is OPEN or ADMITTED.

An Episode that is CLOSED or CANCELLED cannot receive new Encounters.

The create operation supports optional transaction control so higher-level
workflow services can create an Encounter atomically with other changes.
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.encounter.exceptions import (
    EncounterAlreadyClosedError,
    EncounterNotFoundError,
    EpisodeNotFoundError,
    EpisodeNotOpenError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.encounter.models import (
    Encounter,
    EncounterStatus,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.staff.repository import StaffRepository


class EncounterService:
    """
    Business logic for Encounters.
    """

    def __init__(
        self,
        repository: EncounterRepository,
        episode_repository: EpisodeRepository,
        staff_repository: StaffRepository,
    ) -> None:
        self.repository = repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_encounter(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        staff_id: UUID,
        title: str,
        commit: bool = True,
    ) -> Encounter:
        """
        Create a new professional Encounter.

        A newly created Encounter starts OPEN.

        The Episode must:

        - belong to the authenticated Hospital;
        - be OPEN or ADMITTED.

        CLOSED and CANCELLED Episodes cannot receive new Encounters.

        Parameters
        ----------
        commit:
            When True, persist the transaction immediately.

            When False, flush the Encounter but leave transaction
            ownership to the calling service.
        """

        # --------------------------------------------------------------
        # Retrieve Episode within hospital context
        # --------------------------------------------------------------

        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )

        if episode is None:
            raise EpisodeNotFoundError()

        # --------------------------------------------------------------
        # Validate Episode lifecycle
        # --------------------------------------------------------------

        if episode.status not in (
            EpisodeStatus.OPEN,
            EpisodeStatus.ADMITTED,
        ):
            raise EpisodeNotOpenError()

        # --------------------------------------------------------------
        # Validate Staff
        # --------------------------------------------------------------

        staff = self.staff_repository.get_by_id(
            staff_id,
        )

        if staff is None:
            raise StaffNotFoundError()

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError()

        # --------------------------------------------------------------
        # Create Encounter
        # --------------------------------------------------------------

        encounter = Encounter(
            episode_id=episode_id,
            staff_id=staff_id,
            title=title,
            status=EncounterStatus.OPEN,
            started_at=datetime.now(UTC),
            ended_at=None,
        )

        self.repository.create(
            encounter=encounter,
        )

        # --------------------------------------------------------------
        # Transaction Handling
        # --------------------------------------------------------------

        if commit:
            self.repository.save()
        else:
            self.repository.db.flush()

        self.repository.refresh(
            encounter,
        )

        return encounter

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------

    def close_encounter(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> Encounter:
        """
        Close an open Encounter.

        The Encounter must:

        - exist within the authenticated Hospital;
        - currently be OPEN.

        Closing an Encounter records the end timestamp and preserves
        the Encounter as historical clinical activity.
        """

        encounter = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError()

        if encounter.status == EncounterStatus.CLOSED:
            raise EncounterAlreadyClosedError()

        encounter.status = EncounterStatus.CLOSED
        encounter.ended_at = datetime.now(UTC)

        self.repository.save()

        self.repository.refresh(
            encounter,
        )

        return encounter

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_encounter(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> Encounter:
        """
        Retrieve an Encounter within the authenticated Hospital.
        """

        encounter = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError()

        return encounter

    # ------------------------------------------------------------------
    # Episode Encounters
    # ------------------------------------------------------------------

    def list_episode_encounters(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> list[Encounter]:
        """
        Return all Encounters belonging to an Episode
        within the authenticated Hospital.
        """

        return self.repository.list_by_episode(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )