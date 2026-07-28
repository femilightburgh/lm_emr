"""
========================================================================

LIGHTBURGH EMR

Patient API Router

========================================================================

Purpose
-------

Defines the HTTP endpoints for patient management.

Responsibilities
----------------

• Register new patients
• Retrieve a patient by ID
• List all patients
• Update patient information

The router is responsible only for HTTP request/response handling.
Business logic is delegated to the PatientService.

========================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.patients.repositories.patient_repository import PatientRepository
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
    PatientListResponse,
    PatientResponse,
    UpdatePatientRequest,
)
from app.modules.patients.services.patient_service import PatientService


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


# ----------------------------------------------------------------------
# Dependency Injection
# ----------------------------------------------------------------------

def get_patient_service(
    db: Session = Depends(get_db),
) -> PatientService:
    """
    Create a PatientService instance with its required dependencies.
    """

    repository = PatientRepository(db)
    return PatientService(repository)


# ----------------------------------------------------------------------
# Create Patient
# ----------------------------------------------------------------------

@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
)
async def create_patient(
    request: CreatePatientRequest,
    service: PatientService = Depends(get_patient_service),
):
    """
    Register a new patient.
    """

    return service.create_patient(request)


# ----------------------------------------------------------------------
# List Patients
# ----------------------------------------------------------------------

@router.get(
    "",
    response_model=PatientListResponse,
    summary="List or search patients",
)
async def list_patients(
    hospital_number: str | None = Query(
        default=None,
        description="Search by hospital number",
    ),
    name: str | None = Query(
        default=None,
        description="Search by patient's first name, last name, or full name",
    ),
    service: PatientService = Depends(get_patient_service),
):
    """
    Retrieve all patients or search by hospital number or name.
    """

    if hospital_number or name:
        patients = service.search_patients(
            hospital_number=hospital_number,
            name=name,
        )
    else:
        patients = service.list_patients()

    return PatientListResponse(
        total=len(patients),
        items=patients,
    )


# ----------------------------------------------------------------------
# Get Patient
# ----------------------------------------------------------------------

@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by ID",
)
async def get_patient(
    patient_id: UUID,
    service: PatientService = Depends(get_patient_service),
):
    """
    Retrieve a patient by their unique identifier.
    """

    return service.get_patient(patient_id)


# ----------------------------------------------------------------------
# Update Patient
# ----------------------------------------------------------------------

@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
)
async def update_patient(
    patient_id: UUID,
    request: UpdatePatientRequest,
    service: PatientService = Depends(get_patient_service),
):
    """
    Update an existing patient's information.
    """

    return service.update_patient(
        patient_id,
        request,
    )