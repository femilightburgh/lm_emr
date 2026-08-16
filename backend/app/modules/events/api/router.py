"""
==============================================================================
LIGHTBURGH EMR

Clinical Event API Router
==============================================================================

Exposes HTTP endpoints for recording and retrieving Clinical Events.

Business logic belongs in ClinicalEventService.
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

from app.modules.events.exceptions import (
    EncounterNotFoundError,
    EventNotFoundError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.schemas import (
    ClinicalEventResponse,
    CreateClinicalEventRequest,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)


router = APIRouter(
    prefix="/events",
    tags=["Clinical Events"],
)


# ============================================================================
# Dependencies
# ============================================================================

def get_clinical_event_service(
    db: Session = Depends(get_db),
) -> ClinicalEventService:
    """
    Build a ClinicalEventService with its required dependencies.
    """

    return ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )


# ============================================================================
# Create Clinical Event
# ============================================================================

@router.post(
    "",
    response_model=ClinicalEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a Clinical Event",
)
def create_clinical_event(
    request: CreateClinicalEventRequest,
    context: RequestContext = Depends(get_request_context),
    service: ClinicalEventService = Depends(
        get_clinical_event_service,
    ),
):
    """
    Record a clinical action performed within an Encounter.
    """

    try:
        event = service.create_event(
            context=context,
            encounter_id=request.encounter_id,
            event_type=request.event_type,
            performed_by=request.performed_by,
            occurred_at=request.occurred_at,
            payload=request.payload,
        )

        return ClinicalEventResponse.model_validate(event)

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Staff member does not belong to the authenticated Hospital."
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


# ============================================================================
# Retrieve Clinical Event
# ============================================================================

@router.get(
    "/{event_id}",
    response_model=ClinicalEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a Clinical Event",
)
def get_clinical_event(
    event_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: ClinicalEventService = Depends(
        get_clinical_event_service,
    ),
):
    """
    Retrieve a single Clinical Event belonging to the
    authenticated Hospital.
    """

    try:
        event = service.get_event(
            context=context,
            event_id=event_id,
        )

        return ClinicalEventResponse.model_validate(event)

    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Event not found.",
        ) from exc


# ============================================================================
# List Encounter Events
# ============================================================================

@router.get(
    "/encounters/{encounter_id}",
    response_model=list[ClinicalEventResponse],
    status_code=status.HTTP_200_OK,
    summary="List Clinical Events for an Encounter",
)
def list_encounter_events(
    encounter_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: ClinicalEventService = Depends(
        get_clinical_event_service,
    ),
):
    """
    Return the Clinical Events visible to the authenticated
    Hospital for an Encounter.

    Events are returned in clinical occurrence order.
    """

    events = service.list_encounter_events(
        context=context,
        encounter_id=encounter_id,
    )

    return [
        ClinicalEventResponse.model_validate(event)
        for event in events
    ]