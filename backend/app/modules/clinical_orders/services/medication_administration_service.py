"""
==============================================================================
LIGHTBURGH EMR

Medication Administration Service
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
    MedicationDoseStatus,
)
from app.modules.clinical_orders.exceptions import (
    MedicationAdministrationEpisodeError,
    MedicationAdministrationStaffHospitalMismatchError,
    MedicationAdministrationStaffNotFoundError,
    MedicationDoseAlreadyAdministeredError,
    MedicationDoseCannotBeAdministeredError,
    MedicationDoseNotFoundError,
)
from app.modules.clinical_orders.models import (
    MedicationAdministration,
)
from app.modules.clinical_orders.repositories import (
    MedicationAdministrationRepository,
    MedicationTreatmentRepository,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.staff.repository import StaffRepository


class MedicationAdministrationService:
    """
    Business logic for recording inpatient medication administration.
    """

    def __init__(
        self,
        *,
        repository: MedicationAdministrationRepository,
        treatment_repository: MedicationTreatmentRepository,
        episode_repository: EpisodeRepository,
        staff_repository: StaffRepository,
    ) -> None:
        self.repository = repository
        self.treatment_repository = treatment_repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        staff = self.staff_repository.get_by_user_account_id(
            hospital_id=context.hospital_id,
            user_account_id=context.user_id,
        )

        if staff is None:
            raise MedicationAdministrationStaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise MedicationAdministrationStaffHospitalMismatchError(
                "Staff member belongs to another hospital.",
            )

        return staff

    def list_episode_doses(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        from_time: datetime,
        to_time: datetime,
    ):
        """
        Return scheduled medication doses for an admitted Episode.
        """

        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )

        if episode is None:
            raise MedicationDoseNotFoundError(
                "Episode not found.",
            )

        if episode.status != EpisodeStatus.ADMITTED:
            raise MedicationAdministrationEpisodeError(
                "Medication queue requires an admitted Episode.",
            )

        doses = self.treatment_repository.list_doses_for_episode(
            episode_id=episode.id,
            from_time=from_time,
            to_time=to_time,
        )

        return doses

    def record_administration(
        self,
        *,
        context: RequestContext,
        dose_id: UUID,
        status: MedicationAdministrationStatus,
        administered_at: datetime | None = None,
        dose_given: str | None = None,
        reason: str | None = None,
        notes: str | None = None,
    ) -> MedicationAdministration:
        """
        Record one nursing outcome for a scheduled medication dose.
        """

        staff = self._get_authenticated_staff(
            context=context,
        )

        dose = self.repository.get_dose(
            dose_id=dose_id,
        )

        if dose is None:
            raise MedicationDoseNotFoundError(
                "Medication dose not found.",
            )

        treatment = dose.treatment

        if treatment is None:
            raise MedicationDoseCannotBeAdministeredError(
                "Medication treatment could not be resolved.",
            )

        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=treatment.episode_id,
        )

        if episode is None:
            raise MedicationAdministrationEpisodeError(
                "Episode not found.",
            )

        if episode.status != EpisodeStatus.ADMITTED:
            raise MedicationAdministrationEpisodeError(
                "Medication administration requires an admitted Episode.",
            )

        existing = self.repository.get_by_dose_id(
            dose_id=dose.id,
        )

        if existing is not None:
            raise MedicationDoseAlreadyAdministeredError(
                "Medication dose has already been administered.",
            )

        if dose.status == MedicationDoseStatus.CANCELLED:
            raise MedicationDoseCannotBeAdministeredError(
                "Cancelled medication doses cannot be administered.",
            )

        now = datetime.now(UTC)

        if dose.scheduled_at > now:
            raise MedicationDoseCannotBeAdministeredError(
                "Medication dose cannot be administered before "
                "its scheduled time.",
            )

        if administered_at is None:
            administered_at = now

        administration = MedicationAdministration(
            dose_id=dose.id,
            administered_by=staff.id,
            status=status,
            administered_at=administered_at,
            dose_given=(
                dose_given.strip()
                if dose_given is not None and dose_given.strip()
                else None
            ),
            reason=(
                reason.strip()
                if reason is not None and reason.strip()
                else None
            ),
            notes=(
                notes.strip()
                if notes is not None and notes.strip()
                else None
            ),
        )

        self.repository.create(
            administration=administration,
        )

        if status == MedicationAdministrationStatus.GIVEN:
            dose.status = MedicationDoseStatus.GIVEN

        elif status == MedicationAdministrationStatus.HELD:
            dose.status = MedicationDoseStatus.HELD

        elif status == MedicationAdministrationStatus.MISSED:
            dose.status = MedicationDoseStatus.MISSED

        self.repository.flush()

        return administration
