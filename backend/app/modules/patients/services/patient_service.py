"""
==============================================================================
LIGHTBURGH EMR

Patient Service

==============================================================================

Purpose
-------

Contains the business logic for patient management.

Responsibilities
----------------
• Register patients.
• Prevent duplicate hospital numbers.
• Retrieve patients.
• Search patients.
• Update patient demographics.

Business rules belong here.

Persistence belongs in repositories.

HTTP concerns belong in routers.

==============================================================================
"""

from uuid import UUID

from fastapi import HTTPException, status

from app.core.context import RequestContext
from app.modules.patients.models import Patient
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
    UpdatePatientRequest,
)


class PatientService:
    """
    Business logic for Patient management.
    """

    def __init__(
        self,
        repository: PatientRepository,
    ) -> None:
        self.repository = repository

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_patient(
        self,
        *,
        context: RequestContext,
        request: CreatePatientRequest,
    ) -> Patient:
        """
        Register a new patient.
        """

        existing_patient = self.repository.get_by_hospital_number(
            hospital_number=request.hospital_number,
        )

        if existing_patient is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital number already exists.",
            )

        patient = Patient(
            hospital_id=context.hospital_id,
            **request.model_dump(),
        )

        return self.repository.create(
            patient,
        )

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_patient(
        self,
        patient_id: UUID,
    ) -> Patient:
        """
        Retrieve a Patient.
        """

        patient = self.repository.get_by_id(
            patient_id,
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        return patient

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_patients(
        self,
    ) -> list[Patient]:
        """
        Retrieve all Patients.
        """

        return self.repository.get_all()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_patients(
        self,
        *,
        hospital_number: str | None = None,
        name: str | None = None,
    ) -> list[Patient]:
        """
        Search Patients.
        """

        return self.repository.search(
            hospital_number=hospital_number,
            name=name,
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_patient(
        self,
        patient_id: UUID,
        request: UpdatePatientRequest,
    ) -> Patient:
        """
        Update an existing Patient.
        """

        patient = self.get_patient(
            patient_id,
        )

        update_data = request.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(
                patient,
                field,
                value,
            )

        return self.repository.update(
            patient,
        )