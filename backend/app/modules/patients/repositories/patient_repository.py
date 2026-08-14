
"""
==============================================================================
LIGHTBURGH EMR

Patient Repository
==============================================================================

Purpose
-------
Provides persistence operations for Patient entities.

Responsibilities
----------------
- Create patients
- Retrieve patients
- Update patients
- Delete patients
- Enforce hospital-scoped patient queries
==============================================================================
"""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.patients.models import Patient


class PatientRepository:
    """
    Repository responsible for database operations on Patient entities.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, patient: Patient) -> Patient:
        """
        Persist a new patient.
        """
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_by_id(
        self,
        hospital_id: UUID,
        patient_id: UUID,
    ) -> Patient | None:
        """
        Retrieve a patient by ID within a specific hospital.
        """
        result = self.db.execute(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.hospital_id == hospital_id,
            )
        )
        return result.scalar_one_or_none()

    def get_by_hospital_number(
        self,
        hospital_id: UUID,
        hospital_number: str,
    ) -> Patient | None:
        """
        Retrieve a patient by hospital number within a specific hospital.
        """
        result = self.db.execute(
            select(Patient).where(
                Patient.hospital_id == hospital_id,
                Patient.hospital_number == hospital_number,
            )
        )
        return result.scalar_one_or_none()

    def get_all(
        self,
        hospital_id: UUID,
    ) -> list[Patient]:
        """
        Retrieve all patients belonging to a specific hospital.
        """
        result = self.db.execute(
            select(Patient)
            .where(Patient.hospital_id == hospital_id)
            .order_by(
                Patient.last_name,
                Patient.first_name,
            )
        )
        return list(result.scalars().all())

    def search(
        self,
        hospital_id: UUID,
        hospital_number: str | None = None,
        name: str | None = None,
    ) -> list[Patient]:
        """
        Search patients by hospital number or name within a hospital.
        """
        query = select(Patient).where(
            Patient.hospital_id == hospital_id
        )

        if hospital_number:
            query = query.where(
                Patient.hospital_number == hospital_number
            )

        if name:
            search = f"%{name.lower()}%"

            full_name = func.lower(
                Patient.first_name
                + " "
                + Patient.last_name
            )

            query = query.where(
                or_(
                    func.lower(Patient.first_name).like(search),
                    func.lower(Patient.last_name).like(search),
                    full_name.like(search),
                )
            )

        query = query.order_by(
            Patient.last_name,
            Patient.first_name,
        )

        result = self.db.execute(query)

        return list(result.scalars().all())

    def update(self, patient: Patient) -> Patient:
        """
        Persist changes made to a patient.
        """
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete(self, patient: Patient) -> None:
        """
        Delete a patient.
        """
        self.db.delete(patient)
        self.db.commit()
