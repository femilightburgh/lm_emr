"""
==============================================================================
LIGHTBURGH EMR

Vitals API Router
==============================================================================

Exposes HTTP endpoints for recording patient vital signs.

HTTP concerns remain in this router.
Business logic belongs in VitalsService.
Clinical event persistence belongs in ClinicalEventService.
==============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.db.session import get_db

from app.modules.events.exceptions import (
    EncounterNotFoundError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.vitals.schemas import (
    CreateVitalsRequest,
    VitalsResponse,
)
from app.modules.vitals.services import (
    VitalsService,
)


router = APIRouter(
    prefix="/vitals",
    tags=["Vitals"],
)


# ============================================================================
# Dependencies
# ============================================================================

def get_vitals_service(
    db: Session = Depends(get_db),
) -> VitalsService:
    """
    Build a VitalsService with its required dependencies.
    """

    event_service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    return VitalsService(
        event_service=event_service,
    )


# ============================================================================
# Record Vitals
# ============================================================================

@router.post(
    "",
    response_model=VitalsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Patient Vitals",
)
def record_vitals(
    request: CreateVitalsRequest,
    context: RequestContext = Depends(get_request_context),
    service: VitalsService = Depends(get_vitals_service),
):
    """
    Record patient vital signs within an Encounter.
    """

    try:
        event = service.record_vitals(
            context=context,
            request=request,
        )

        return VitalsResponse.model_validate(event)

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