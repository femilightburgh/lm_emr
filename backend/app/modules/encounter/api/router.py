"""
LIGHTBURGH EMR

Encounter API Router

==============================================================================

Exposes HTTP endpoints for managing professional Encounters.

Business logic belongs in EncounterService.
Database access belongs in repositories.
HTTP concerns remain in this router.

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
    EncounterAlreadyClosedError,
    EncounterNotFoundError,
    EpisodeNotFoundError,
    EpisodeNotOpenError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.schemas.request import CreateEncounterRequest
from app.modules.encounter.schemas.response import EncounterResponse
from app.modules.encounter.services.encounter_service import EncounterService
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.staff.repository import StaffRepository


router = APIRouter(
    prefix="/encounters",
    tags=["Encounters"],
)


# ============================================================================
# Dependencies
# ============================================================================

def get_encounter_service(
    db: Session = Depends(get_db),
) -> EncounterService:
    """
    Build an EncounterService with its required dependencies.
    """

    return EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )


# ============================================================================
# Create Encounter
# ============================================================================

@router.post(
    "",
    response_model=EncounterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start an Encounter",
)
def create_encounter(
    request: CreateEncounterRequest,
    context: RequestContext = Depends(get_request_context),
    service: EncounterService = Depends(get_encounter_service),
):
    """
    Start a new professional Encounter.
    """

    try:
        encounter = service.create_encounter(
            context=context,
            episode_id=request.episode_id,
            staff_id=request.staff_id,
            title=request.title,
        )

        return EncounterResponse.model_validate(encounter)

    except EpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except EpisodeNotOpenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encounters can only be created for open episodes.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff member does not belong to the authenticated Hospital.",
        ) from exc


# ============================================================================
# Retrieve Encounter
# ============================================================================

@router.get(
    "/{encounter_id}",
    response_model=EncounterResponse,
    summary="Retrieve an Encounter",
)
def get_encounter(
    encounter_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: EncounterService = Depends(get_encounter_service),
):
    """
    Retrieve an Encounter by its identifier.
    """

    try:
        encounter = service.get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        return EncounterResponse.model_validate(encounter)

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc


# ============================================================================
# Close Encounter
# ============================================================================

@router.post(
    "/{encounter_id}/close",
    response_model=EncounterResponse,
    status_code=status.HTTP_200_OK,
    summary="Close an Encounter",
)
def close_encounter(
    encounter_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: EncounterService = Depends(get_encounter_service),
):
    """
    Close an open Encounter.
    """

    try:
        encounter = service.close_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        return EncounterResponse.model_validate(encounter)

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except EncounterAlreadyClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Encounter is already closed.",
        ) from exc


# ============================================================================
# Episode Encounters
# ============================================================================

@router.get(
    "/episode/{episode_id}",
    response_model=list[EncounterResponse],
    summary="List Encounters for an Episode",
)
def list_episode_encounters(
    episode_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: EncounterService = Depends(get_encounter_service),
):
    """
    List all Encounters belonging to an Episode
    within the authenticated Hospital.
    """

    encounters = service.list_episode_encounters(
        context=context,
        episode_id=episode_id,
    )

    return [
        EncounterResponse.model_validate(encounter)
        for encounter in encounters
    ]