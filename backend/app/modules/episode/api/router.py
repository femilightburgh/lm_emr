"""
==============================================================================
LIGHTBURGH EMR

Episode API Router

==============================================================================

Purpose
-------

Exposes HTTP endpoints for managing Episodes of Care.

Business logic belongs in EpisodeService.

Database access belongs in repositories.

The router should remain as thin as possible.

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
    EpisodeAlreadyCancelledError,
    EpisodeAlreadyClosedError,
    EpisodeAlreadyExistsError,
    EpisodeNotFoundError,
    PatientNotFoundError,
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
    Build the EpisodeService with its complete production
    dependency graph.
    """

    repository = EpisodeRepository(db)

    patient_repository = PatientRepository(db)

    number_generator = EpisodeNumberGenerator(
        repository=repository,
    )

    encounter_repository = EncounterRepository(db)

    event_service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    staff_repository = StaffRepository(
        session=db,
    )

    return EpisodeService(
        repository=repository,
        patient_repository=patient_repository,
        number_generator=number_generator,
        encounter_repository=encounter_repository,
        event_service=event_service,
        staff_repository=staff_repository,
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
    Retrieve an Episode by its identifier.
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
# Close Episode
# ============================================================================


@router.post(
    "/{episode_id}/close",
    response_model=EpisodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Close an Episode of Care",
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
    Close an open Episode of Care.

    The Episode must belong to the authenticated Hospital
    and must currently have an OPEN status.

    Once closed, the Episode receives a closed_at timestamp
    and cannot be closed again.
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
    status_code=status.HTTP_200_OK,
    summary="Cancel an Episode of Care",
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
    Cancel an open Episode of Care.

    The Episode must belong to the authenticated Hospital
    and must currently have an OPEN status.

    Once cancelled, the Episode receives a CANCELLED status.
    The closed_at timestamp remains unset because cancellation
    is distinct from completing the Episode.
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


# ============================================================================
# List Patient Episodes
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