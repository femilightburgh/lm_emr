
"""
==============================================================================
LIGHTBURGH EMR

Patient Service
==============================================================================

Purpose
-------
Contains business logic for Patient management.

Responsibilities
----------------
- Register patients
- Prevent duplicate hospital numbers
- Retrieve patients
- Search patients
- Update patient demographics

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

    def create_patient(
        self,
        *,
        context: RequestContext,
        request: CreatePatientRequest,
    ) -> Patient:
        """
        Register a new patient within the current hospital.
        """

        existing_patient = self.repository.get_by_hospital_number(
            hospital_id=context.hospital_id,
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

        return self.repository.create(patient)

    def get_patient(
        self,
        *,
        context: RequestContext,
        patient_id: UUID,
    ) -> Patient:
        """
        Retrieve a patient within the current hospital.
        """

        patient = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            patient_id=patient_id,
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        return patient

    def list_patients(
        self,
        *,
        context: RequestContext,
    ) -> list[Patient]:
        """
        Retrieve all patients within the current hospital.
        """

        return self.repository.get_all(
            hospital_id=context.hospital_id,
        )

    def search_patients(
        self,
        *,
        context: RequestContext,
        hospital_number: str | None = None,
        name: str | None = None,
    ) -> list[Patient]:
        """
        Search patients within the current hospital.
        """

        return self.repository.search(
            hospital_id=context.hospital_id,
            hospital_number=hospital_number,
            name=name,
        )

    def update_patient(
        self,
        *,
        context: RequestContext,
        patient_id: UUID,
        request: UpdatePatientRequest,
    ) -> Patient:
        """
        Update an existing patient within the current hospital.
        """

        patient = self.get_patient(
            context=context,
            patient_id=patient_id,
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

        return self.repository.update(patient)
