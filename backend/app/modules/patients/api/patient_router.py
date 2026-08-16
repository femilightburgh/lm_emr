"""
==============================================================================
LIGHTBURGH EMR

Patient API Router
==============================================================================

Purpose
-------
Defines the HTTP endpoints for patient management.

Authentication and authorization are enforced at the API boundary.

Business logic belongs in PatientService.

Persistence belongs in PatientRepository.

HTTP concerns belong here.
==============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.core.security.authorization import (
    require_permission,
)
from app.db.session import get_db

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
    PatientListResponse,
    PatientResponse,
    UpdatePatientRequest,
)
from app.modules.patients.services.patient_service import (
    PatientService,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


# =============================================================================
# Dependency Injection
# =============================================================================


def get_patient_service(
    db: Session = Depends(get_db),
) -> PatientService:
    """
    Build a PatientService.
    """

    repository = PatientRepository(db)

    return PatientService(
        repository=repository,
    )


# =============================================================================
# Create Patient
# =============================================================================


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
)
async def create_patient(
    request: CreatePatientRequest,
    current_user=Depends(
        require_permission("patient.create"),
    ),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: PatientService = Depends(
        get_patient_service,
    ),
):
    """
    Register a new patient.

    Requires:
        patient.create
    """

    return service.create_patient(
        context=context,
        request=request,
    )


# =============================================================================
# List / Search Patients
# =============================================================================


@router.get(
    "",
    response_model=PatientListResponse,
    summary="List patients",
)
async def list_patients(
    hospital_number: str | None = Query(
        default=None,
    ),
    name: str | None = Query(
        default=None,
    ),
    current_user=Depends(
        require_permission("patient.read"),
    ),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: PatientService = Depends(
        get_patient_service,
    ),
):
    """
    List or search patients within the current hospital.

    Requires:
        patient.read
    """

    if hospital_number or name:
        patients = service.search_patients(
            context=context,
            hospital_number=hospital_number,
            name=name,
        )
    else:
        patients = service.list_patients(
            context=context,
        )

    return PatientListResponse(
        total=len(patients),
        items=patients,
    )


# =============================================================================
# Get Patient
# =============================================================================


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Retrieve a patient",
)
async def get_patient(
    patient_id: UUID,
    current_user=Depends(
        require_permission("patient.read"),
    ),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: PatientService = Depends(
        get_patient_service,
    ),
):
    """
    Retrieve a patient within the current hospital.

    Requires:
        patient.read
    """

    return service.get_patient(
        context=context,
        patient_id=patient_id,
    )


# =============================================================================
# Update Patient
# =============================================================================


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
)
async def update_patient(
    patient_id: UUID,
    request: UpdatePatientRequest,
    current_user=Depends(
        require_permission("patient.update"),
    ),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: PatientService = Depends(
        get_patient_service,
    ),
):
    """
    Update an existing patient within the current hospital.

    Requires:
        patient.update
    """

    return service.update_patient(
        context=context,
        patient_id=patient_id,
        request=request,
    )