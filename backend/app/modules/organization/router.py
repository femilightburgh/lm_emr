"""
==============================================================================
LIGHTBURGH EMR

Organization Router

==============================================================================

API endpoints for Organization management.

==============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.exceptions import DuplicateResourceException
from app.db.session import get_db
from app.modules.organization.schemas import (
    HospitalCreate,
    HospitalResponse,
)
from app.modules.organization.service import HospitalService

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


def get_hospital_service(
    db: Session = Depends(get_db),
) -> HospitalService:
    """
    Dependency provider for HospitalService.
    """
    return HospitalService(db)


@router.post(
    "",
    response_model=HospitalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital(
    request: HospitalCreate,
    service: HospitalService = Depends(get_hospital_service),
):
    """
    Create a new hospital.
    """
    try:
        return service.create_hospital(request)

    except DuplicateResourceException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )