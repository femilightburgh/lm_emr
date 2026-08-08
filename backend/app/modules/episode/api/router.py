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
from app.modules.episode.exceptions import (
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
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
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
    Build an EpisodeService with its required dependencies.
    """

    repository = EpisodeRepository(db)

    patient_repository = PatientRepository(db)

    number_generator = EpisodeNumberGenerator(
        repository=repository,
    )

    return EpisodeService(
        repository=repository,
        patient_repository=patient_repository,
        number_generator=number_generator,
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