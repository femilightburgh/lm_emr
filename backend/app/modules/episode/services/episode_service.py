"""
==============================================================================
LIGHTBURGH EMR

Episode Service
==============================================================================

Business logic for Episodes of Care.

Responsibilities
----------------
• Create Episodes.
• Generate hospital-scoped Episode numbers.
• Retrieve Episodes.
• Check Episodes in for clinical care.
• List the nursing queue.
• Start nursing intake.
• Create the Nursing Encounter.
• Route Episodes to departments.
• Admit Episodes.
• Assign the managing doctor during admission.
• Close Episodes.
• Cancel Episodes.
• List Episodes belonging to a Patient.

Database access belongs in repositories.

HTTP concerns belong in routers.

Clinical lifecycle and operational workflow remain separate.
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)
from app.modules.clinical_documents.repositories import (
    ClinicalDocumentRepository,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)

from app.modules.encounter.exceptions import (
    EncounterNotFoundError,
)
from app.modules.encounter.models import (
    Encounter,
    EncounterStatus,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)

from app.modules.episode.exceptions import (
    DoctorReviewEncounterRequiredError,
    DepartmentHospitalMismatchError,
    DepartmentInactiveError,
    DepartmentNotFoundError,
    EncounterNotBelongingToEpisodeError,
    EncounterNotOpenError,
    EpisodeAlreadyAdmittedError,
    EpisodeAlreadyCancelledError,
    EpisodeAlreadyClosedError,
    EpisodeAlreadyExistsError,
    EpisodeAlreadyInNursingError,
    EpisodeAlreadyRoutedError,
    EpisodeNotAwaitingCheckInError,
    InvalidConsultationDispositionError,
    InvalidWardReviewDispositionError,
    EpisodeNotFoundError,
    WardReviewEncounterRequiredError,
    WardReviewDispositionDetailsRequiredError,
    EpisodeNotInNursingError,
    EpisodeNotOpenError,
    EpisodeNotWaitingForNursingError,
    NursingIntakeNotSignedError,
    PatientNotFoundError,
    StaffHospitalMismatchError,
    StaffNotDoctorError,
    StaffNotFoundError,
)

from app.modules.episode.models import (
    Episode,
    EpisodeDisposition,
    EpisodeDispositionType,
    EpisodeFlowStatus,
    EpisodeStatus,
)

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.repositories.episode_disposition_repository import (
    EpisodeDispositionRepository,
)

from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)

from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.organization.department_repository import (
    DepartmentRepository,
)
from app.modules.organization.enums import DepartmentStatus

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)

from app.modules.staff.enums import Profession
from app.modules.staff.repository import StaffRepository


class EpisodeService:
    """
    Business logic for Episodes of Care.
    """

    def __init__(
        self,
        *,
        repository: EpisodeRepository,
        patient_repository: PatientRepository,
        number_generator: EpisodeNumberGenerator,
        encounter_service: EncounterService,
        event_service: ClinicalEventService,
        staff_repository: StaffRepository,
        disposition_repository: EpisodeDispositionRepository,
        department_repository: DepartmentRepository | None = None,
    ) -> None:
        self.repository = repository
        self.patient_repository = patient_repository
        self.number_generator = number_generator
        self.encounter_service = encounter_service
        self.event_service = event_service
        self.staff_repository = staff_repository
        self.disposition_repository = disposition_repository

        if department_repository is None:
            department_repository = DepartmentRepository(
                repository.db,
            )

        self.department_repository = department_repository

        self.clinical_document_repository = (
            ClinicalDocumentRepository(
                repository.db,
            )
        )

        self.clinical_order_repository = ClinicalOrderRepository(
            repository.db,
        )

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _get_episode(
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

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        """
        Resolve the authenticated UserAccount to its Staff profile.
        """

        staff = self.staff_repository.get_by_user_account_id(
            hospital_id=context.hospital_id,
            user_account_id=context.user_id,
        )

        if staff is None:
            raise StaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError(
                "Staff member belongs to another hospital.",
            )

        return staff

    def _ensure_episode_not_closed_or_cancelled(
        self,
        episode: Episode,
    ) -> None:
        """
        Ensure the Episode is still operationally modifiable.
        """

        if episode.status == EpisodeStatus.CLOSED:
            raise EpisodeAlreadyClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise EpisodeAlreadyCancelledError()

    def _get_nursing_encounter(
        self,
        *,
        episode: Episode,
    ) -> Encounter | None:
        """
        Return the latest Nursing Intake Encounter belonging to the Episode.

        Nursing Encounters are created by start_nursing() with the
        explicit title "Nursing Intake".
        """

        nursing_encounters = [
            encounter
            for encounter in episode.encounters
            if encounter.title == "Nursing Intake"
        ]

        if not nursing_encounters:
            return None

        return max(
            nursing_encounters,
            key=lambda encounter: encounter.started_at,
        )

    def _ensure_nursing_intake_signed(
        self,
        *,
        context: RequestContext,
        episode: Episode,
    ) -> None:
        """
        Ensure the latest Nursing Intake document is signed.

        Routing is not permitted until nursing has completed and signed
        the Nursing Intake Clinical Document.
        """

        nursing_encounter = self._get_nursing_encounter(
            episode=episode,
        )

        if nursing_encounter is None:
            raise NursingIntakeNotSignedError(
                "Nursing Encounter not found.",
            )

        nursing_intake = (
            self.clinical_document_repository.get_latest_version(
                hospital_id=context.hospital_id,
                encounter_id=nursing_encounter.id,
                document_type=ClinicalDocumentType.NURSING_INTAKE,
            )
        )

        if nursing_intake is None:
            raise NursingIntakeNotSignedError(
                "Nursing Intake must be completed before the Episode "
                "can be routed.",
            )

        if nursing_intake.status != ClinicalDocumentStatus.SIGNED:
            raise NursingIntakeNotSignedError(
                "Nursing Intake must be signed before the Episode "
                "can be routed.",
            )

    # =========================================================================
    # Create
    # =========================================================================

    def create_episode(
        self,
        *,
        context: RequestContext,
        patient_id: UUID,
        title: str,
    ) -> Episode:
        """
        Create a new Episode of Care.

        Business Rules
        --------------

        • Patient must exist.
        • Patient must belong to the authenticated Hospital.
        • Episode number is generated by the platform.
        • Episode starts OPEN.
        • Episode starts AWAITING_CHECK_IN.
        • Episode has no managing doctor.
        """

        patient = self.patient_repository.get_by_id(
            hospital_id=context.hospital_id,
            patient_id=patient_id,
        )

        if patient is None:
            raise PatientNotFoundError()

        if patient.hospital_id != context.hospital_id:
            raise PatientNotFoundError()

        episode_number = self.number_generator.generate(
            hospital_id=context.hospital_id,
        )

        existing = self.repository.get_by_episode_number(
            hospital_id=context.hospital_id,
            episode_number=episode_number,
        )

        if existing is not None:
            raise EpisodeAlreadyExistsError()

        episode = Episode(
            hospital_id=context.hospital_id,
            patient_id=patient_id,
            managing_doctor_id=None,
            episode_number=episode_number,
            title=title,
            status=EpisodeStatus.OPEN,
            flow_status=EpisodeFlowStatus.AWAITING_CHECK_IN,
            checked_in_at=None,
            checked_in_by=None,
            triaged_at=None,
            triaged_by=None,
            routed_at=None,
            routed_by=None,
            current_department_id=None,
            opened_at=datetime.now(UTC),
            closed_at=None,
        )

        try:
            self.repository.create(
                episode=episode,
            )

            self.repository.save()

            self.repository.refresh(
                episode,
            )

            return episode

        except Exception:
            self.repository.rollback()
            raise

    # =========================================================================
    # Retrieve
    # =========================================================================

    def get_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> Episode:
        """
        Retrieve an Episode within the authenticated Hospital.
        """

        return self._get_episode(
            context=context,
            episode_id=episode_id,
        )

    # =========================================================================
    # Reception Check-In
    # =========================================================================

    def check_in_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> Episode:
        """
        Check in an Episode for clinical care.

        State transition:

            AWAITING_CHECK_IN
                    ↓
            WAITING_FOR_NURSING
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        self._ensure_episode_not_closed_or_cancelled(
            episode,
        )

        if episode.flow_status != EpisodeFlowStatus.AWAITING_CHECK_IN:
            raise EpisodeNotAwaitingCheckInError()

        staff = self._get_authenticated_staff(
            context=context,
        )

        episode.flow_status = EpisodeFlowStatus.WAITING_FOR_NURSING
        episode.checked_in_at = datetime.now(UTC)
        episode.checked_in_by = staff.id

        try:
            self.repository.save()

            self.repository.refresh(
                episode,
            )

            return episode

        except Exception:
            self.repository.rollback()
            raise

    # =========================================================================
    # Nursing Queue
    # =========================================================================

    def list_nursing_queue(
        self,
        *,
        context: RequestContext,
    ) -> list[Episode]:
        """
        Return Episodes currently waiting for nursing attention.

        Includes:

            WAITING_FOR_NURSING
            NURSING_IN_PROGRESS

        The queue is hospital-scoped.
        """

        return self.repository.list_nursing_queue(
            hospital_id=context.hospital_id,
        )

    # =========================================================================
    # Doctor Clinic Queue
    # =========================================================================

    def list_doctor_clinic_queue(
        self,
        *,
        context: RequestContext,
    ) -> list[Episode]:
        """
        Return open Episodes routed to the Doctor workflow.
        """

        return self.repository.list_doctor_clinic_queue(
            hospital_id=context.hospital_id,
        )



    # =========================================================================
    # Nursing Inpatients
    # =========================================================================

    def list_admitted_episodes(
        self,
        *,
        context: RequestContext,
    ) -> list[Episode]:
        """
        Return Episodes currently on admission within the Hospital.
        """

        return self.repository.list_admitted_episodes(
            hospital_id=context.hospital_id,
        )


    # =========================================================================
    # Doctor Ward Queue
    # =========================================================================

    def list_doctor_ward_queue(
        self,
        *,
        context: RequestContext,
    ) -> list[Episode]:
        """
        Return admitted Episodes managed by the authenticated Doctor.
        """

        staff = self._get_authenticated_staff(
            context=context,
        )

        return self.repository.list_doctor_ward_queue(
            hospital_id=context.hospital_id,
            managing_doctor_id=staff.id,
        )


    # =========================================================================
    # Start Nursing
    # =========================================================================

    def start_nursing(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> Episode:
        """
        Begin nursing intake for an Episode.

        State transition:

            WAITING_FOR_NURSING
                    ↓
            NURSING_IN_PROGRESS

        Starting nursing also creates the Nursing Encounter.

        The Episode state change and Encounter creation are committed
        atomically as one transaction.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        self._ensure_episode_not_closed_or_cancelled(
            episode,
        )

        if episode.flow_status == EpisodeFlowStatus.NURSING_IN_PROGRESS:
            raise EpisodeAlreadyInNursingError()

        if episode.flow_status != EpisodeFlowStatus.WAITING_FOR_NURSING:
            raise EpisodeNotWaitingForNursingError()

        staff = self._get_authenticated_staff(
            context=context,
        )

        try:
            episode.flow_status = (
                EpisodeFlowStatus.NURSING_IN_PROGRESS
            )

            self.encounter_service.create_encounter(
                context=context,
                episode_id=episode.id,
                staff_id=staff.id,
                title="Nursing Intake",
                commit=False,
            )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(
            episode,
        )

        return episode

    # =========================================================================
    # Route Episode
    # =========================================================================

    def route_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        department_id: UUID,
    ) -> Episode:
        """
        Route a nursing-completed Episode to a hospital department.

        Business Rules
        --------------

        • Episode must exist.
        • Episode must belong to the authenticated Hospital.
        • Episode must currently be NURSING_IN_PROGRESS.
        • Episode must not already be routed.
        • Nursing Intake must exist.
        • Latest Nursing Intake must be SIGNED.
        • Department must exist.
        • Department must belong to the authenticated Hospital.
        • Department must be active.
        • Authenticated user must have a Staff profile.
        • Routing Staff is recorded.
        • Routing timestamp is recorded.
        • Department is recorded as current department.
        • Episode moves to ROUTED.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        self._ensure_episode_not_closed_or_cancelled(
            episode,
        )

        if episode.flow_status == EpisodeFlowStatus.ROUTED:
            raise EpisodeAlreadyRoutedError()

        if episode.flow_status != EpisodeFlowStatus.NURSING_IN_PROGRESS:
            raise EpisodeNotInNursingError()

        # ------------------------------------------------------------------
        # Nursing Completion
        # ------------------------------------------------------------------

        self._ensure_nursing_intake_signed(
            context=context,
            episode=episode,
        )

        # ------------------------------------------------------------------
        # Department
        # ------------------------------------------------------------------

        department = self.department_repository.get_by_id(
            department_id,
        )

        if department is None:
            raise DepartmentNotFoundError()

        if department.hospital_id != context.hospital_id:
            raise DepartmentHospitalMismatchError()

        if department.status != DepartmentStatus.ACTIVE:
            raise DepartmentInactiveError()

        # ------------------------------------------------------------------
        # Routing Staff
        # ------------------------------------------------------------------

        staff = self._get_authenticated_staff(
            context=context,
        )

        # ------------------------------------------------------------------
        # Complete Nursing Encounter
        # ------------------------------------------------------------------

        encounters = self.encounter_service.list_episode_encounters(
            context=context,
            episode_id=episode.id,
        )

        nursing_encounter = next(
            (
                encounter
                for encounter in encounters
                if (
                    encounter.title == "Nursing Intake"
                    and encounter.status == EncounterStatus.OPEN
                )
            ),
            None,
        )

        if nursing_encounter is None:
            raise EncounterNotFoundError(
                "Open Nursing Intake encounter not found.",
            )

        try:
            self.encounter_service.close_encounter(
                context=context,
                encounter_id=nursing_encounter.id,
                commit=False,
            )

            # --------------------------------------------------------------
            # Route
            # --------------------------------------------------------------

            episode.current_department_id = department.id
            episode.routed_at = datetime.now(UTC)
            episode.routed_by = staff.id
            episode.flow_status = EpisodeFlowStatus.ROUTED

            self.repository.save()

            self.repository.refresh(
                episode,
            )

            return episode

        except Exception:
            self.repository.rollback()
            raise

    # =========================================================================
    # Complete Doctor Consultation
    # =========================================================================

    def complete_consultation(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        encounter_id: UUID,
        disposition: str,
    ) -> Episode:
        """
        Complete an outpatient Doctor Consultation.

        Supported disposition:

            COMPLETE

        Completing the consultation closes the Doctor Consultation
        encounter while keeping the Episode OPEN.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        if episode.status != EpisodeStatus.OPEN:
            raise EpisodeNotOpenError()

        if disposition != "COMPLETE":
            raise InvalidConsultationDispositionError(
                "Unsupported consultation disposition.",
            )

        encounter = self.encounter_service.get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError()

        if encounter.episode_id != episode.id:
            raise EncounterNotBelongingToEpisodeError()

        if encounter.title != "Doctor Consultation":
            raise InvalidConsultationDispositionError(
                "Only a Doctor Consultation can be completed "
                "through this workflow.",
            )

        if encounter.status != EncounterStatus.OPEN:
            raise EncounterNotOpenError()

        documents = (
            self.clinical_document_repository.list_by_encounter(
                hospital_id=context.hospital_id,
                encounter_id=encounter.id,
            )
        )

        has_signed_initial_clerking = any(
            document.document_type
            == ClinicalDocumentType.INITIAL_CLERKING
            and document.status
            == ClinicalDocumentStatus.SIGNED
            for document in documents
        )

        if not has_signed_initial_clerking:
            raise InvalidConsultationDispositionError(
                "A signed Initial Clerking is required "
                "before completing the Doctor Consultation.",
            )

        outstanding_investigations = (
            self.clinical_order_repository
            .list_outstanding_investigation_orders_for_episode(
                hospital_id=context.hospital_id,
                episode_id=episode.id,
            )
        )

        completed_at = datetime.now(UTC)

        try:
            encounter.status = EncounterStatus.CLOSED
            encounter.ended_at = completed_at

            if outstanding_investigations:
                episode.flow_status = (
                    EpisodeFlowStatus.AWAITING_INVESTIGATIONS
                )

            self.repository.db.flush()
            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(
            episode,
        )

        return episode


    # =========================================================================
    # Complete Doctor Review
    # =========================================================================

    def complete_doctor_review(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        encounter_id: UUID,
    ) -> Episode:
        """
        Complete an outpatient Doctor Review.

        The Doctor Review Encounter is closed while the Episode remains
        OPEN and returns to ROUTED for any subsequent clinical action.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        if episode.status == EpisodeStatus.CLOSED:
            raise EpisodeAlreadyClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise EpisodeAlreadyCancelledError()

        if episode.status != EpisodeStatus.OPEN:
            raise InvalidConsultationDispositionError(
                "Doctor Review requires an OPEN Episode.",
            )

        if episode.flow_status != EpisodeFlowStatus.AWAITING_REVIEW:
            raise InvalidConsultationDispositionError(
                "Doctor Review can only be completed when the Episode "
                "is awaiting review.",
            )

        encounter = self.encounter_service.get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError()

        if encounter.episode_id != episode.id:
            raise EncounterNotBelongingToEpisodeError()

        if encounter.title != "Doctor Review":
            raise DoctorReviewEncounterRequiredError(
                "Only a Doctor Review encounter can be completed "
                "through this workflow.",
            )

        if encounter.status != EncounterStatus.OPEN:
            raise EncounterNotOpenError()

        completed_at = datetime.now(UTC)

        try:
            encounter.status = EncounterStatus.CLOSED
            encounter.ended_at = completed_at
            episode.flow_status = EpisodeFlowStatus.ROUTED

            self.repository.db.flush()
            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(
            episode,
        )

        return episode


    # =========================================================================
    # Complete Ward Review
    # =========================================================================

    def complete_ward_review(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        encounter_id: UUID,
        disposition: EpisodeDispositionType,
        details: str | None = None,
    ) -> Episode:
        """
        Complete an inpatient Ward Review.

        The Ward Review Encounter is closed for every valid disposition.

        A DISCHARGE disposition also closes the Episode.

        TRANSFER, REFERRAL, and OTHER require details and do not
        change the Episode lifecycle.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        if episode.status == EpisodeStatus.CLOSED:
            raise EpisodeAlreadyClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise EpisodeAlreadyCancelledError()

        if episode.status != EpisodeStatus.ADMITTED:
            raise InvalidWardReviewDispositionError(
                "Ward Review disposition requires an admitted Episode.",
            )

        encounter = self.encounter_service.get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError()

        if encounter.episode_id != episode.id:
            raise EncounterNotBelongingToEpisodeError()

        if encounter.title != "Ward Review":
            raise WardReviewEncounterRequiredError(
                "Only a Ward Review encounter can be completed "
                "through this workflow.",
            )

        if encounter.status != EncounterStatus.OPEN:
            raise EncounterNotOpenError()

        normalized_details = (
            details.strip()
            if details is not None
            else None
        )

        if disposition in {
            EpisodeDispositionType.TRANSFER,
            EpisodeDispositionType.REFERRAL,
            EpisodeDispositionType.OTHER,
        } and not normalized_details:
            raise WardReviewDispositionDetailsRequiredError(
                "Details are required for this Ward Review disposition.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        completed_at = datetime.now(UTC)

        record = EpisodeDisposition(
            hospital_id=context.hospital_id,
            episode_id=episode.id,
            encounter_id=encounter.id,
            disposition=disposition,
            details=normalized_details,
            decided_by=staff.id,
            decided_at=completed_at,
        )

        try:
            self.disposition_repository.create(
                disposition=record,
            )

            self.encounter_service.close_encounter(
                context=context,
                encounter_id=encounter.id,
                commit=False,
            )

            if disposition == EpisodeDispositionType.DISCHARGE:
                episode.status = EpisodeStatus.CLOSED
                episode.closed_at = completed_at

            self.repository.db.flush()
            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(
            episode,
        )

        return episode


    # =========================================================================
    # Admit Episode
    # =========================================================================

    def admit_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        encounter_id: UUID,
    ) -> Episode:
        """
        Admit an open Episode into inpatient care.

        Admission must occur through an OPEN Encounter belonging
        to the Episode.

        The doctor associated with the Encounter becomes the
        managing doctor.

        State transition:

            OPEN
              ↓
           ADMITTED

        The Episode state transition, managing doctor assignment,
        and EPISODE_ADMITTED clinical event are committed atomically.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        if episode.status == EpisodeStatus.ADMITTED:
            raise EpisodeAlreadyAdmittedError()

        if episode.status == EpisodeStatus.CLOSED:
            raise EpisodeAlreadyClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise EpisodeAlreadyCancelledError()

        if episode.status != EpisodeStatus.OPEN:
            raise EpisodeNotOpenError()

        encounter = self.encounter_service.get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError()

        if encounter.episode_id != episode.id:
            raise EncounterNotBelongingToEpisodeError()

        if encounter.status != EncounterStatus.OPEN:
            raise EncounterNotOpenError()

        staff = self.staff_repository.get_by_id(
            encounter.staff_id,
        )

        if staff is None:
            raise StaffNotFoundError(
                "Admission clinician not found.",
            )

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError(
                "Admission clinician belongs to another hospital.",
            )

        employment = self.staff_repository.get_active_employment(
            staff.id,
        )

        if employment is None:
            raise StaffNotDoctorError(
                "Admission clinician has no active employment.",
            )

        if employment.profession != Profession.DOCTOR:
            raise StaffNotDoctorError(
                "Only a doctor can become the managing doctor of an Episode.",
            )

        admitted_at = datetime.now(UTC)

        try:
            episode.status = EpisodeStatus.ADMITTED
            episode.managing_doctor_id = staff.id

            encounter.status = EncounterStatus.CLOSED
            encounter.ended_at = admitted_at

            self.repository.db.flush()

            self.event_service.create_event(
                context=context,
                encounter_id=encounter.id,
                event_type=EventType.EPISODE_ADMITTED,
                performed_by=encounter.staff_id,
                occurred_at=admitted_at,
                payload={
                    "episode_id": str(episode.id),
                    "managing_doctor_id": str(staff.id),
                },
                commit=False,
            )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(
            episode,
        )

        return episode

    # =========================================================================
    # Close Episode
    # =========================================================================

    def close_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> Episode:
        """
        Close an Episode.

        Allowed transitions:

            OPEN → CLOSED
            ADMITTED → CLOSED
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        if episode.status == EpisodeStatus.CLOSED:
            raise EpisodeAlreadyClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise EpisodeAlreadyCancelledError()

        episode.status = EpisodeStatus.CLOSED
        episode.closed_at = datetime.now(UTC)

        try:
            self.repository.save()

            self.repository.refresh(
                episode,
            )

            return episode

        except Exception:
            self.repository.rollback()
            raise

    # =========================================================================
    # Cancel Episode
    # =========================================================================

    def cancel_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> Episode:
        """
        Cancel an Episode.

        Only OPEN Episodes may be cancelled.

        State transition:

            OPEN → CANCELLED
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        if episode.status == EpisodeStatus.CLOSED:
            raise EpisodeAlreadyClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise EpisodeAlreadyCancelledError()

        if episode.status == EpisodeStatus.ADMITTED:
            raise EpisodeAlreadyAdmittedError()

        if episode.status != EpisodeStatus.OPEN:
            raise EpisodeNotOpenError()

        episode.status = EpisodeStatus.CANCELLED

        try:
            self.repository.save()

            self.repository.refresh(
                episode,
            )

            return episode

        except Exception:
            self.repository.rollback()
            raise

    # =========================================================================
    # Patient Episodes
    # =========================================================================

    def list_patient_episodes(
        self,
        *,
        context: RequestContext,
        patient_id: UUID,
    ) -> list[Episode]:
        """
        List Episodes belonging to a Patient within the authenticated
        Hospital.

        Tenant isolation is enforced by the repository.
        """

        return self.repository.list_by_patient(
            hospital_id=context.hospital_id,
            patient_id=patient_id,
        )