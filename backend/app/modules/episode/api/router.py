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

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
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
    EpisodeNotFoundError,
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

from app.modules.episode.schemas import (
    CreateEpisodeRequest,
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

    encounter_repository = EncounterRepository(
        db,
    )

    event_service = ClinicalEventService(
        repository=ClinicalEventRepository(
            db,
        ),
    )

    staff_repository = StaffRepository(
        session=db,
    )

    department_repository = DepartmentRepository(
        db,
    )

    return EpisodeService(
        repository=repository,
        patient_repository=patient_repository,
        number_generator=number_generator,
        encounter_repository=encounter_repository,
        event_service=event_service,
        staff_repository=staff_repository,
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