"""
==============================================================================
LIGHTBURGH EMR

Episode API Router
==============================================================================

HTTP endpoints for Episodes of Care.

Business logic belongs in EpisodeService.

Database access belongs in repositories.

The router remains responsible for HTTP concerns only.
==============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.db.session import get_db

from app.modules.encounter.exceptions import (
    EncounterNotFoundError,
)

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)

from app.modules.encounter.services.encounter_service import (
    EncounterService,
)

from app.modules.episode.exceptions import (
    DepartmentHospitalMismatchError,
    DepartmentInactiveError,
    DepartmentNotFoundError,
    EpisodeAlreadyAdmittedError,
    EpisodeAlreadyCancelledError,
    EpisodeAlreadyClosedError,
    EpisodeAlreadyExistsError,
    EpisodeAlreadyInNursingError,
    EpisodeAlreadyRoutedError,
    EpisodeNotAwaitingCheckInError,
    InvalidConsultationDispositionError,
    DoctorReviewEncounterRequiredError,
    InvalidWardReviewDispositionError,
    EpisodeNotFoundError,
    WardReviewEncounterRequiredError,
    WardReviewDispositionDetailsRequiredError,
    EpisodeNotInNursingError,
    EpisodeNotOpenError,
    EpisodeNotWaitingForNursingError,
    PatientNotFoundError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.repositories.episode_disposition_repository import (
    EpisodeDispositionRepository,
)

from app.modules.episode.schemas import (
    CompleteConsultationRequest,
    CompleteDoctorReviewRequest,
    CompleteWardReviewRequest,
    CreateEpisodeRequest,
    DoctorQueueItemResponse,
    EpisodeResponse,
)

from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)

from app.modules.episode.services.episode_service import (
    EpisodeService,
)

from app.modules.events.repositories import (
    ClinicalEventRepository,
)

from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.organization.department_repository import (
    DepartmentRepository,
)

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)

from app.modules.staff.repository import (
    StaffRepository,
)


router = APIRouter(
    prefix="/episodes",
    tags=["Episodes"],
)


# ============================================================================
# Dependencies
# ============================================================================


def get_episode_service(
    db: Session = Depends(get_db),
) -> EpisodeService:
    """
    Build the complete EpisodeService dependency graph.
    """

    repository = EpisodeRepository(
        db,
    )

    patient_repository = PatientRepository(
        db,
    )

    number_generator = EpisodeNumberGenerator(
        repository=repository,
    )

    staff_repository = StaffRepository(
        session=db,
    )

    encounter_repository = EncounterRepository(
        db,
    )

    encounter_service = EncounterService(
        repository=encounter_repository,
        episode_repository=repository,
        staff_repository=staff_repository,
    )

    event_service = ClinicalEventService(
        repository=ClinicalEventRepository(
            db,
        ),
    )

    department_repository = DepartmentRepository(
        db,
    )

    disposition_repository = EpisodeDispositionRepository(
        db,
    )

    return EpisodeService(
        repository=repository,
        patient_repository=patient_repository,
        number_generator=number_generator,
        encounter_service=encounter_service,
        event_service=event_service,
        staff_repository=staff_repository,
        disposition_repository=disposition_repository,
        department_repository=department_repository,
    )


# ============================================================================
# Create Episode
# ============================================================================


@router.post(
    "",
    response_model=EpisodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an Episode of Care",
)
def create_episode(
    request: CreateEpisodeRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Create a new Episode of Care.
    """

    try:
        episode = service.create_episode(
            context=context,
            patient_id=request.patient_id,
            title=request.title,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except PatientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        ) from exc

    except EpisodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode already exists.",
        ) from exc


# ============================================================================
# Retrieve Episode
# ============================================================================


@router.get(
    "/{episode_id}",
    response_model=EpisodeResponse,
    summary="Retrieve an Episode",
)
def get_episode(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Retrieve an Episode by identifier.
    """

    try:
        episode = service.get_episode(
            context=context,
            episode_id=episode_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc


# ============================================================================
# Reception Check-In
# ============================================================================


@router.post(
    "/{episode_id}/check-in",
    response_model=EpisodeResponse,
    summary="Check in an Episode",
)
def check_in_episode(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Receptionist check-in.

    Moves:

        AWAITING_CHECK_IN
                ↓
        WAITING_FOR_NURSING
    """

    try:
        episode = service.check_in_episode(
            context=context,
            episode_id=episode_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot be checked in.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot be checked in.",
        ) from exc

    except EpisodeNotAwaitingCheckInError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is not awaiting check-in.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user does not have a Staff profile.",
        ) from exc



# ============================================================================
# Nursing Inpatients
# ============================================================================


@router.get(
    "/queue/nursing/inpatients",
    response_model=list[EpisodeResponse],
    summary="List admitted patients for Nursing",
)
def list_nursing_inpatients(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Return Episodes currently on admission within the Hospital.
    """

    episodes = service.list_admitted_episodes(
        context=context,
    )

    return [
        EpisodeResponse.model_validate(
            episode,
        )
        for episode in episodes
    ]


# ============================================================================
# Nursing Queue
# ============================================================================


@router.get(
    "/queue/nursing",
    response_model=list[EpisodeResponse],
    summary="List the nursing queue",
)
def list_nursing_queue(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Return Episodes currently waiting for or undergoing nursing intake.
    """

    episodes = service.list_nursing_queue(
        context=context,
    )

    return [
        EpisodeResponse.model_validate(
            episode,
        )
        for episode in episodes
    ]


# ============================================================================
# Doctor Clinic Queue
# ============================================================================


@router.get(
    "/queue/doctor/clinic",
    response_model=list[DoctorQueueItemResponse],
    summary="List the doctor's clinic queue",
)
def list_doctor_clinic_queue(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Return open Episodes routed to the Doctor workflow.
    """

    episodes = service.list_doctor_clinic_queue(
        context=context,
    )

    return [
        DoctorQueueItemResponse(
            id=episode.id,
            patient_id=episode.patient_id,
            patient_name=(
                f"{episode.patient.first_name} "
                f"{episode.patient.last_name}"
            ),
            hospital_number=episode.patient.hospital_number,
            episode_number=episode.episode_number,
            title=episode.title,
            status=episode.status,
            flow_status=episode.flow_status,
            managing_doctor_id=episode.managing_doctor_id,
            checked_in_at=episode.checked_in_at,
            routed_at=episode.routed_at,
        )
        for episode in episodes
    ]


# ============================================================================
# Doctor Ward Queue
# ============================================================================


@router.get(
    "/queue/doctor/ward",
    response_model=list[DoctorQueueItemResponse],
    summary="List the doctor's ward queue",
)
def list_doctor_ward_queue(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Return admitted Episodes managed by the authenticated Doctor.
    """

    episodes = service.list_doctor_ward_queue(
        context=context,
    )

    return [
        DoctorQueueItemResponse(
            id=episode.id,
            patient_id=episode.patient_id,
            patient_name=(
                f"{episode.patient.first_name} "
                f"{episode.patient.last_name}"
            ),
            hospital_number=episode.patient.hospital_number,
            episode_number=episode.episode_number,
            title=episode.title,
            status=episode.status,
            flow_status=episode.flow_status,
            managing_doctor_id=episode.managing_doctor_id,
            checked_in_at=episode.checked_in_at,
            routed_at=episode.routed_at,
        )
        for episode in episodes
    ]


# ============================================================================
# Start Nursing
# ============================================================================


@router.post(
    "/{episode_id}/nursing/start",
    response_model=EpisodeResponse,
    summary="Start nursing intake",
)
def start_nursing(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Start nursing intake.

    Moves:

        WAITING_FOR_NURSING
                ↓
        NURSING_IN_PROGRESS
    """

    try:
        episode = service.start_nursing(
            context=context,
            episode_id=episode_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot enter nursing.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot enter nursing.",
        ) from exc

    except EpisodeAlreadyInNursingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is already in nursing.",
        ) from exc

    except EpisodeNotWaitingForNursingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is not waiting for nursing.",
        ) from exc


# ============================================================================
# Route Episode
# ============================================================================


@router.post(
    "/{episode_id}/route",
    response_model=EpisodeResponse,
    summary="Route an Episode to a department",
)
def route_episode(
    episode_id: UUID,
    department_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Route a nursing-completed Episode to a department.
    """

    try:
        episode = service.route_episode(
            context=context,
            episode_id=episode_id,
            department_id=department_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot be routed.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot be routed.",
        ) from exc

    except EpisodeAlreadyRoutedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode has already been routed.",
        ) from exc

    except EpisodeNotInNursingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is not currently in nursing.",
        ) from exc

    except DepartmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        ) from exc

    except DepartmentHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Department belongs to another hospital.",
        ) from exc

    except DepartmentInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department is inactive.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user does not have a Staff profile.",
        ) from exc



# ============================================================================
# Complete Doctor Consultation
# ============================================================================


@router.post(
    "/{episode_id}/complete-consultation",
    response_model=EpisodeResponse,
    summary="Complete an outpatient Doctor Consultation",
)
def complete_consultation(
    episode_id: UUID,
    payload: CompleteConsultationRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Complete an outpatient Doctor Consultation.
    """

    try:
        episode = service.complete_consultation(
            context=context,
            episode_id=episode_id,
            encounter_id=payload.encounter_id,
            disposition=payload.disposition,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot be completed.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot be completed.",
        ) from exc

    except EpisodeNotOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is not open.",
        ) from exc

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except EncounterNotBelongingToEpisodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encounter does not belong to the Episode.",
        ) from exc

    except EncounterNotOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encounter is not open.",
        ) from exc

    except InvalidConsultationDispositionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Complete Doctor Review
# ============================================================================


@router.post(
    "/{episode_id}/complete-doctor-review",
    response_model=EpisodeResponse,
    summary="Complete an outpatient Doctor Review",
)
def complete_doctor_review(
    episode_id: UUID,
    payload: CompleteDoctorReviewRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Complete an outpatient Doctor Review.
    """

    try:
        episode = service.complete_doctor_review(
            context=context,
            episode_id=episode_id,
            encounter_id=payload.encounter_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except (
        EncounterNotBelongingToEpisodeError,
        EncounterNotOpenError,
        DoctorReviewEncounterRequiredError,
        InvalidConsultationDispositionError,
        EpisodeAlreadyClosedError,
        EpisodeAlreadyCancelledError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Complete Ward Review
# ============================================================================


@router.post(
    "/{episode_id}/complete-ward-review",
    response_model=EpisodeResponse,
    summary="Complete an inpatient Ward Review",
)
def complete_ward_review(
    episode_id: UUID,
    payload: CompleteWardReviewRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Complete an inpatient Ward Review.
    """

    try:
        episode = service.complete_ward_review(
            context=context,
            episode_id=episode_id,
            encounter_id=payload.encounter_id,
            disposition=payload.disposition,
            details=payload.details,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot complete a Ward Review.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot complete a Ward Review.",
        ) from exc

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except EncounterNotBelongingToEpisodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encounter does not belong to the Episode.",
        ) from exc

    except EncounterNotOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encounter is not open.",
        ) from exc

    except (
        InvalidWardReviewDispositionError,
        WardReviewEncounterRequiredError,
        WardReviewDispositionDetailsRequiredError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Admit Episode
# ============================================================================


@router.post(
    "/{episode_id}/admit",
    response_model=EpisodeResponse,
    summary="Admit an Episode",
)
def admit_episode(
    episode_id: UUID,
    encounter_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Admit an Episode into inpatient care.
    """

    try:
        episode = service.admit_episode(
            context=context,
            episode_id=episode_id,
            encounter_id=encounter_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyAdmittedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is already admitted.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot be admitted.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot be admitted.",
        ) from exc

    except EpisodeNotOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is not open.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission clinician not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admission clinician belongs to another hospital.",
        ) from exc


# ============================================================================
# Close Episode
# ============================================================================


@router.post(
    "/{episode_id}/close",
    response_model=EpisodeResponse,
    summary="Close an Episode",
)
def close_episode(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Close an Episode.
    """

    try:
        episode = service.close_episode(
            context=context,
            episode_id=episode_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is already closed.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled episodes cannot be closed.",
        ) from exc


# ============================================================================
# Cancel Episode
# ============================================================================


@router.post(
    "/{episode_id}/cancel",
    response_model=EpisodeResponse,
    summary="Cancel an Episode",
)
def cancel_episode(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    Cancel an open Episode.
    """

    try:
        episode = service.cancel_episode(
            context=context,
            episode_id=episode_id,
        )

        return EpisodeResponse.model_validate(
            episode,
        )

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed episodes cannot be cancelled.",
        ) from exc

    except EpisodeAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Episode is already cancelled.",
        ) from exc

    except EpisodeAlreadyAdmittedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admitted episodes cannot be cancelled.",
        ) from exc


# ============================================================================
# Patient Episodes
# ============================================================================


@router.get(
    "/patient/{patient_id}",
    response_model=list[EpisodeResponse],
    summary="List Episodes for a Patient",
)
def list_patient_episodes(
    patient_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: EpisodeService = Depends(
        get_episode_service,
    ),
):
    """
    List all Episodes belonging to a Patient
    within the authenticated Hospital.
    """

    try:
        episodes = service.list_patient_episodes(
            context=context,
            patient_id=patient_id,
        )

        return [
            EpisodeResponse.model_validate(
                episode,
            )
            for episode in episodes
        ]

    except PatientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        ) from exc