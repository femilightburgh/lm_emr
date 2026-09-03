from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.context import RequestContext
from app.modules.diagnoses.enums import (
    DiagnosisCertainty,
    DiagnosisType,
)
from app.modules.diagnoses.exceptions import (
    ClinicalDiagnosisEncounterClosedError,
    ClinicalDiagnosisEncounterNotFoundError,
    ClinicalDiagnosisEpisodeCancelledError,
    ClinicalDiagnosisEpisodeNotFoundError,
    ClinicalDiagnosisEpisodeClosedError,
    ClinicalDiagnosisStaffHospitalMismatchError,
    ClinicalDiagnosisStaffNotFoundError,
)
from app.modules.diagnoses.models import ClinicalDiagnosis
from app.modules.diagnoses.repositories import (
    ClinicalDiagnosisRepository,
)
from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.repositories import TerminologyRepository
from app.modules.encounter.models import EncounterStatus
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.staff.repository import StaffRepository


class ClinicalDiagnosisService:
    """
    Business logic for structured Clinical Diagnoses.
    """

    def __init__(
        self,
        *,
        repository: ClinicalDiagnosisRepository,
        event_service: ClinicalEventService,
        encounter_repository: EncounterRepository,
        episode_repository: EpisodeRepository,
        staff_repository: StaffRepository,
        terminology_repository: TerminologyRepository,
    ) -> None:
        self.repository = repository
        self.event_service = event_service
        self.encounter_repository = encounter_repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository
        self.terminology_repository = terminology_repository

    def _get_encounter(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ):
        encounter = self.encounter_repository.get_by_id(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise ClinicalDiagnosisEncounterNotFoundError(
                "Encounter not found.",
            )

        return encounter

    def _get_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ):
        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )

        if episode is None:
            raise ClinicalDiagnosisEpisodeNotFoundError(
                "Episode not found.",
            )

        return episode

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
            raise ClinicalDiagnosisStaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise ClinicalDiagnosisStaffHospitalMismatchError(
                "Staff member belongs to another hospital.",
            )

        return staff

    def _resolve_terminology_concept(
        self,
        *,
        code_system: str | None,
        code: str | None,
        diagnosis_name: str,
    ):
        if code_system is None and code is None:
            return None

        if code_system is None or code is None:
            raise ValueError(
                "code_system and code must be provided together.",
            )

        try:
            system = TerminologySystem(code_system)
        except ValueError as exc:
            raise ValueError(
                f"Unsupported terminology system: {code_system}",
            ) from exc

        concept = self.terminology_repository.get_by_system_and_code(
            system=system,
            code=code.strip(),
        )

        if concept is None or not concept.active:
            raise ValueError(
                "Terminology concept was not found or is inactive.",
            )

        return concept

    def create_diagnosis(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
        diagnosis_name: str,
        diagnosis_type: DiagnosisType,
        certainty: DiagnosisCertainty,
        code_system: str | None = None,
        code: str | None = None,
        onset_date=None,
        notes: str | None = None,
    ) -> ClinicalDiagnosis:
        """
        Create a structured diagnosis and its clinical event atomically.
        """

        if not isinstance(diagnosis_type, DiagnosisType):
            raise ValueError("Invalid diagnosis type.")

        if not isinstance(certainty, DiagnosisCertainty):
            raise ValueError("Invalid diagnosis certainty.")

        diagnosis_name = diagnosis_name.strip()
        if not diagnosis_name:
            raise ValueError("Diagnosis name is required.")

        terminology_concept = self._resolve_terminology_concept(
            code_system=code_system,
            code=code,
            diagnosis_name=diagnosis_name,
        )

        if terminology_concept is not None:
            code_system = terminology_concept.system.value
            code = terminology_concept.code
            diagnosis_name = terminology_concept.display_name

        encounter = self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        if encounter.status != EncounterStatus.OPEN:
            raise ClinicalDiagnosisEncounterClosedError(
                "Diagnoses cannot be recorded on a closed Encounter.",
            )

        episode = self._get_episode(
            context=context,
            episode_id=encounter.episode_id,
        )

        if episode.status == EpisodeStatus.CLOSED:
            raise ClinicalDiagnosisEpisodeClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise ClinicalDiagnosisEpisodeCancelledError()

        if episode.status not in (
            EpisodeStatus.OPEN,
            EpisodeStatus.ADMITTED,
        ):
            raise ClinicalDiagnosisEpisodeClosedError(
                "Episode is not available for diagnosis.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        diagnosed_at = datetime.now(UTC)

        diagnosis = ClinicalDiagnosis(
            id=uuid4(),
            encounter_id=encounter.id,
            episode_id=episode.id,
            diagnosis_name=diagnosis_name,
            code_system=code_system,
            code=code,
            diagnosis_type=diagnosis_type,
            certainty=certainty,
            onset_date=onset_date,
            diagnosed_by=staff.id,
            diagnosed_at=diagnosed_at,
            resolved_at=None,
            notes=notes,
        )

        self.repository.create(
            diagnosis=diagnosis,
        )

        self.event_service.create_event(
            context=context,
            encounter_id=encounter.id,
            event_type=EventType.DIAGNOSIS_RECORDED,
            performed_by=staff.id,
            occurred_at=diagnosed_at,
            payload={
                "clinical_diagnosis_id": str(diagnosis.id),
                "diagnosis_name": diagnosis.diagnosis_name,
                "code_system": diagnosis.code_system,
                "code": diagnosis.code,
                "diagnosis_type": diagnosis.diagnosis_type.value,
                "certainty": diagnosis.certainty.value,
            },
        )

        self.repository.save()
        self.repository.refresh(diagnosis)

        return diagnosis

    def get_diagnosis(
        self,
        *,
        context: RequestContext,
        diagnosis_id: UUID,
    ) -> ClinicalDiagnosis:
        diagnosis = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            diagnosis_id=diagnosis_id,
        )

        if diagnosis is None:
            raise ClinicalDiagnosisNotFoundError(
                "Clinical diagnosis not found.",
            )

        return diagnosis

    def list_episode_diagnoses(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> list[ClinicalDiagnosis]:
        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        return self.repository.list_by_episode(
            hospital_id=context.hospital_id,
            episode_id=episode.id,
        )

    def list_encounter_diagnoses(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> list[ClinicalDiagnosis]:
        encounter = self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        return self.repository.list_by_encounter(
            hospital_id=context.hospital_id,
            encounter_id=encounter.id,
        )
