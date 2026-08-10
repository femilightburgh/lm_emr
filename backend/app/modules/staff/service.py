"""
==============================================================================
LIGHTBURGH EMR

Staff Service
==============================================================================

Purpose
-------
Implements the business logic for the Staff module.

The StaffService coordinates business rules while delegating all database
operations to the StaffRepository.

Architecture
------------
                FastAPI Router
                       │
                       ▼
                 StaffService
                       │
                       ▼
                StaffRepository
                       │
                       ▼
               SQLAlchemy ORM
                       │
                       ▼
                  PostgreSQL

Responsibilities
----------------
• Register staff members.
• Retrieve staff records.
• Update staff information.
• Enforce business rules.
• Coordinate persistence.

Notes
-----
• Services never access SQLAlchemy directly.
• Services never raise HTTPException.
• Services return domain models.
• Database operations belong to the repository.
==============================================================================
"""

from uuid import UUID

from app.modules.organization.repository import HospitalRepository
from app.modules.staff.exceptions import (
    DuplicateStaffNumberError,
    HospitalNotFoundError,
    InvalidEmploymentDateError,
    NoCurrentEmploymentError,
    StaffNotFoundError,
)
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import (
    StaffCreate,
    StaffEmploymentClose,
    StaffUpdate,
)
from app.modules.staff.employment_repository import (
    StaffEmploymentRepository,
)
from app.modules.staff.models import (
    Staff,
    StaffEmployment,
)


class StaffService:
    """
    Business service responsible for staff management.
    """

    def __init__(
        self,
        repository: StaffRepository,
        hospital_repository: HospitalRepository,
        employment_repository: StaffEmploymentRepository,
    ) -> None:
        self.repository = repository
        self.hospital_repository = hospital_repository
        self.employment_repository = employment_repository

    # ======================================================================
    # Public API
    # ======================================================================

    def create_staff(self, data: StaffCreate) -> Staff:
        """
        Register a new staff member and create their initial
        employment period.

        Staff identity and employment history are persisted
        within the same database transaction.
        """

        self._validate_hospital(data.hospital_id)

        self._validate_staff_number(
            hospital_id=data.hospital_id,
            staff_number=data.staff_number,
        )

        self._validate_dates(data)

        staff = self._build_staff(data)

        self.repository.create(staff)

        # Flush so the Staff UUID is available before creating
        # the related employment record.
        self.repository.flush()

        employment = StaffEmployment(
            staff_id=staff.id,
            profession=data.profession,
            employment_status=data.employment_status,
            employment_type=data.employment_type,
            date_employed=data.date_employed,
            date_left=data.date_left,
        )

        self.employment_repository.create(employment)

        self.repository.commit()
        self.repository.refresh(staff)

        return staff

    def get_staff(self, staff_id: UUID) -> Staff:
        """
        Retrieve a staff member by ID.
        """

        staff = self.repository.get_by_id(staff_id)

        if staff is None:
            raise StaffNotFoundError(
                f"Staff '{staff_id}' was not found."
            )

        return staff

    def list_employment_history(
        self,
        staff_id: UUID,
    ) -> list[StaffEmployment]:
        """
        Retrieve the complete employment history for a staff member.

        Results are ordered from most recent employment period
        to oldest.
        """

        # Ensure the staff member exists first.
        self.get_staff(staff_id)

        return self.employment_repository.list_by_staff(
            staff_id,
        )

    def get_current_employment(
        self,
        staff_id: UUID,
    ) -> StaffEmployment | None:
        """
        Retrieve the current employment record for a staff member.
        """

        self.get_staff(staff_id)

        return self.employment_repository.get_current(
            staff_id,
        )

    def close_current_employment(
        self,
        staff_id: UUID,
        data: StaffEmploymentClose,
    ) -> StaffEmployment:
        """
        Close the current employment period for a staff member.
        """

        staff = self.get_staff(staff_id)

        employment = self.employment_repository.get_current(
            staff_id,
        )

        if employment is None:
            raise NoCurrentEmploymentError(
                f"Staff '{staff_id}' has no current employment."
            )

        if data.date_left < employment.date_employed:
            raise InvalidEmploymentDateError(
                "Date left cannot be before employment date."
            )

        employment.date_left = data.date_left
        employment.employment_status = data.employment_status

        self.employment_repository.save(employment)
        self.repository.commit()
        self.repository.refresh(staff)

        return employment

    def list_staff(
        self,
        hospital_id: UUID,
    ) -> list[Staff]:
        """
        Retrieve all staff members for a hospital.
        """

        self._validate_hospital(hospital_id)

        return self.repository.list_staff(hospital_id)

    def update_staff(
        self,
        staff_id: UUID,
        data: StaffUpdate,
    ) -> Staff:
        """
        Update an existing staff member.
        """

        staff = self.get_staff(staff_id)

        for field, value in data.model_dump(
            exclude_unset=True
        ).items():
            setattr(staff, field, value)

        self._validate_dates(staff)

        return self.repository.save(staff)

    # ======================================================================
    # Validation Helpers
    # ======================================================================

    def _validate_hospital(
        self,
        hospital_id: UUID,
    ) -> None:
        """
        Ensure the hospital exists.
        """

        hospital = self.hospital_repository.get_hospital_by_id(
            hospital_id
        )

        if hospital is None:
            raise HospitalNotFoundError(
                f"Hospital '{hospital_id}' does not exist."
            )

    def _validate_staff_number(
        self,
        hospital_id: UUID,
        staff_number: str,
    ) -> None:
        """
        Ensure staff number is unique.
        """

        existing_staff = (
            self.repository.get_by_staff_number(
                hospital_id=hospital_id,
                staff_number=staff_number,
            )
        )

        if existing_staff:
            raise DuplicateStaffNumberError(
                f"Staff number '{staff_number}' already exists."
            )

    def _validate_dates(
        self,
        data: StaffCreate | Staff,
    ) -> None:
        """
        Validate employment dates.
        """

        if (
            data.date_of_birth
            and data.date_employed
            and data.date_employed < data.date_of_birth
        ):
            raise InvalidEmploymentDateError(
                "Employment date cannot be before date of birth."
            )

        if (
            data.date_left
            and data.date_employed
            and data.date_left < data.date_employed
        ):
            raise InvalidEmploymentDateError(
                "Date left cannot be before employment date."
            )

        if (
            data.date_left
            and data.date_of_birth
            and data.date_left < data.date_of_birth
        ):
            raise InvalidEmploymentDateError(
                "Date left cannot be before date of birth."
            )

    # ======================================================================
    # Factory Helpers
    # ======================================================================

    @staticmethod
    def _build_staff(
        data: StaffCreate,
    ) -> Staff:
        """
        Create a Staff ORM object.
        """

        return Staff(
            hospital_id=data.hospital_id,
            staff_number=data.staff_number,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            gender=data.gender,
            date_of_birth=data.date_of_birth,
            phone_number=data.phone_number,
            email=data.email,
            profession=data.profession,
            employment_status=data.employment_status,
            employment_type=data.employment_type,
            date_employed=data.date_employed,
            date_left=data.date_left,
        )