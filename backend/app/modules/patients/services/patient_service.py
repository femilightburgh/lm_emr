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
- Register new patients
- Prevent duplicate hospital numbers
- Retrieve patients
- Update patient demographics

The service layer coordinates repositories and enforces business rules.
It should not contain database-specific implementation details.
==============================================================================
"""

from uuid import UUID

from fastapi import HTTPException, status

from app.modules.patients.models import Patient
from app.modules.patients.repositories.patient_repository import PatientRepository
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
    UpdatePatientRequest,
)


class PatientService:
    """
    Service responsible for patient business logic.
    """

    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def create_patient(
        self,
        request: CreatePatientRequest,
    ) -> Patient:
        """
        Register a new patient.

        Args:
            request: Patient registration request.

        Returns:
            The newly created Patient.

        Raises:
            HTTPException:
                409 if the hospital number already exists.
        """

        existing_patient = self.repository.get_by_hospital_number(
            request.hospital_number
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital number already exists.",
            )

        patient = Patient(**request.model_dump())

        return self.repository.create(patient)

    def get_patient(self, patient_id: UUID) -> Patient:
        """
        Retrieve a patient by ID.

        Raises:
            HTTPException:
                404 if the patient does not exist.
        """

        patient = self.repository.get_by_id(patient_id)

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        return patient

    def list_patients(self) -> list[Patient]:
        """
        Retrieve all registered patients.
        """
        return self.repository.get_all()
    
    def search_patients(
        self,
        hospital_number: str | None = None,
        name: str | None = None,
    ) -> list[Patient]:
        """
        Search patients by hospital number or name.
        """

        return self.repository.search(
            hospital_number=hospital_number,
            name=name,
        )

    def update_patient(
        self,
        patient_id: UUID,
        request: UpdatePatientRequest,
    ) -> Patient:
        """
        Update an existing patient.
        """

        patient = self.get_patient(patient_id)

        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(patient, field, value)

        return self.repository.update(patient)