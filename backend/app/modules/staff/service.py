"""
==============================================================================
LIGHTBURGH EMR

Staff Service
==============================================================================

Purpose
-------
Implements the business logic for the Staff module.

The StaffService coordinates business rules while delegating persistence
operations to the appropriate repositories.

Responsibilities
----------------
• Register staff members.
• Retrieve staff records.
• List staff records.
• Update staff information.
• Manage employment history.
• Link Staff profiles to UserAccount records.
• Enforce staff business rules.

Architecture
------------
FastAPI Router
      │
      ▼
StaffService
      │
      ├───────────────┐
      ▼               ▼
StaffRepository   IdentityRepository
      │
      ▼
SQLAlchemy ORM

Notes
-----
• Services do not access SQLAlchemy directly.
• Services do not raise HTTPException.
• Database operations belong to repositories.
• The service coordinates business rules.
==============================================================================
"""

from datetime import date
from uuid import UUID

from app.modules.identity.repository import IdentityRepository
from app.modules.organization.repository import HospitalRepository
from app.modules.staff.employment_repository import (
    StaffEmploymentRepository,
)
from app.modules.staff.exceptions import (
    CurrentEmploymentExistsError,
    DuplicateStaffNumberError,
    HospitalNotFoundError,
    InvalidEmploymentDateError,
    NoCurrentEmploymentError,
    StaffNotFoundError,
    UserAccountAlreadyLinkedError,
    UserAccountHospitalMismatchError,
)
from app.modules.staff.models import (
    Staff,
    StaffEmployment,
)
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import (
    StaffCreate,
    StaffEmploymentClose,
    StaffEmploymentCreate,
    StaffUpdate,
)


class StaffService:
    """
    Business service responsible for Staff management.
    """

    def __init__(
        self,
        repository: StaffRepository,
        hospital_repository: HospitalRepository,
        employment_repository: StaffEmploymentRepository,
        identity_repository: IdentityRepository | None = None,
    ) -> None:
        self.repository = repository
        self.hospital_repository = hospital_repository
        self.employment_repository = employment_repository
        self.identity_repository = identity_repository

    # =========================================================================
    # Create Staff
    # =========================================================================

    def create_staff(
        self,
        data: StaffCreate,
    ) -> Staff:
        """
        Register a new Staff member and create the initial
        employment period.

        Staff and its initial employment are added to the same
        SQLAlchemy unit of work. The ORM relationship ensures that
        the Staff row is inserted before the StaffEmployment row.
        """

        self._validate_hospital(
            data.hospital_id,
        )

        self._validate_create_dates(
            data,
        )

        existing_staff = (
            self.repository.get_by_staff_number(
                hospital_id=data.hospital_id,
                staff_number=data.staff_number,
            )
        )

        if existing_staff is not None:
            raise DuplicateStaffNumberError(
                f"Staff number '{data.staff_number}' "
                "already exists in this hospital.",
            )

        staff = Staff(
            hospital_id=data.hospital_id,
            staff_number=data.staff_number,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            gender=data.gender,
            date_of_birth=data.date_of_birth,
            phone_number=data.phone_number,
            email=data.email,
        )

        employment = StaffEmployment(
            profession=data.profession,
            employment_status=data.employment_status,
            employment_type=data.employment_type,
            date_employed=data.date_employed,
            date_left=data.date_left,
        )

        # IMPORTANT:
        # Attach the employment through the ORM relationship.
        # SQLAlchemy will establish staff_id automatically and
        # insert Staff before StaffEmployment.
        staff.employments.append(
            employment,
        )

        self.repository.create(
            staff,
        )

        self.repository.flush()

        self.repository.commit()

        return staff

        # Flush so generated IDs and database state are available
        # to the caller, without committing the transaction.
        self.repository.flush()

        return staff

    # =========================================================================
    # Retrieve Staff
    # =========================================================================

    def get_staff(
        self,
        staff_id: UUID,
    ) -> Staff:
        """
        Retrieve a Staff member by ID.
        """

        staff = self.repository.get_by_id(
            staff_id,
        )

        if staff is None:
            raise StaffNotFoundError(
                f"Staff '{staff_id}' was not found.",
            )

        return staff

    def list_staff(
        self,
        hospital_id: UUID,
    ) -> list[Staff]:
        """
        Retrieve all Staff members belonging to a Hospital.
        """

        self._validate_hospital(
            hospital_id,
        )

        return self.repository.list_staff(
            hospital_id,
        )

    # =========================================================================
    # Update Staff
    # =========================================================================

    def update_staff(
        self,
        staff_id: UUID,
        data: StaffUpdate,
    ) -> Staff:
        """
        Update permanent Staff information.

        Employment history is intentionally not modified here.
        """

        staff = self.get_staff(
            staff_id,
        )

        updates = data.model_dump(
            exclude_unset=True,
        )

        for field, value in updates.items():
            setattr(
                staff,
                field,
                value,
            )

        return self.repository.save(
            staff,
        )

    # =========================================================================
    # Link User Account
    # =========================================================================

    def link_user_account(
        self,
        staff_id: UUID,
        user_account_id: UUID,
    ) -> Staff:
        """
        Link a Staff profile to an existing UserAccount.

        Rules
        -----
        • Staff must exist.
        • UserAccount must exist.
        • UserAccount must belong to the same Hospital.
        • A UserAccount can only be linked to one Staff profile.
        • Linking an already-linked account to the same Staff
          profile is idempotent.

        The IdentityRepository is optional for backwards compatibility
        with existing StaffService consumers. The linking operation itself
        requires it.
        """

        if self.identity_repository is None:
            raise RuntimeError(
                "IdentityRepository is required to link "
                "a user account.",
            )

        staff = self.get_staff(
            staff_id,
        )

        user = self.identity_repository.get_user_by_id(
            user_account_id,
        )

        if user is None:
            raise UserAccountHospitalMismatchError(
                "User account was not found.",
            )

        if user.hospital_id != staff.hospital_id:
            raise UserAccountHospitalMismatchError(
                "User account does not belong to the same "
                "hospital as the staff member.",
            )

        existing_staff = (
            self.repository.get_by_user_account_id(
                hospital_id=staff.hospital_id,
                user_account_id=user_account_id,
            )
        )

        if existing_staff is not None:
            if existing_staff.id == staff.id:
                return staff

            raise UserAccountAlreadyLinkedError(
                "User account is already linked to another "
                "staff profile.",
            )

        staff.user_account_id = user_account_id

        staff = self.repository.save(
            staff,
        )

        self.repository.commit()

        return staff

    # =========================================================================
    # Employment History
    # =========================================================================

    def list_employment_history(
        self,
        staff_id: UUID,
    ) -> list[StaffEmployment]:
        """
        Retrieve the complete employment history for a Staff member.
        """

        self.get_staff(
            staff_id,
        )

        return self.employment_repository.list_by_staff(
            staff_id,
        )

    def get_current_employment(
        self,
        staff_id: UUID,
    ) -> StaffEmployment | None:
        """
        Retrieve the current employment record for a Staff member.

        Returns None when there is no current employment.
        """

        self.get_staff(
            staff_id,
        )

        return self.employment_repository.get_current(
            staff_id,
        )

    # =========================================================================
    # Start Employment
    # =========================================================================

    def start_employment(
        self,
        staff_id: UUID,
        data: StaffEmploymentCreate,
    ) -> StaffEmployment:
        """
        Start a new employment period for a Staff member.

        A Staff member cannot have more than one current
        employment period.
        """

        staff = self.get_staff(
            staff_id,
        )

        current_employment = (
            self.employment_repository.get_current(
                staff_id,
            )
        )

        if current_employment is not None:
            raise CurrentEmploymentExistsError(
                "Staff member already has current employment.",
            )

        if (
            staff.date_of_birth is not None
            and data.date_employed < staff.date_of_birth
        ):
            raise InvalidEmploymentDateError(
                "Employment date cannot be before date of birth.",
            )

        employment = StaffEmployment(
            staff_id=staff.id,
            profession=data.profession,
            employment_status=data.employment_status,
            employment_type=data.employment_type,
            date_employed=data.date_employed,
            date_left=None,
        )

        self.employment_repository.create(
            employment,
        )

        # Make the new employment immediately visible to subsequent
        # queries in the same service operation.
        self.employment_repository.session.flush()

        return employment
    # =========================================================================
    # Close Employment
    # =========================================================================

    def close_current_employment(
        self,
        staff_id: UUID,
        data: StaffEmploymentClose,
    ) -> StaffEmployment:
        """
        Close the current employment period for a Staff member.
        """

        staff = self.get_staff(
            staff_id,
        )

        current_employment = (
            self.employment_repository.get_current(
                staff_id,
            )
        )

        if current_employment is None:
            raise NoCurrentEmploymentError(
                "Staff member has no current employment.",
            )

        if data.date_left < current_employment.date_employed:
            raise InvalidEmploymentDateError(
                "Date left cannot be before employment date.",
            )

        if (
            staff.date_of_birth is not None
            and data.date_left < staff.date_of_birth
        ):
            raise InvalidEmploymentDateError(
                "Date left cannot be before date of birth.",
            )

        current_employment.date_left = data.date_left
        current_employment.employment_status = data.employment_status

        return self.employment_repository.save(
            current_employment,
        )

    # =========================================================================
    # Validation Helpers
    # =========================================================================

    def _validate_hospital(
        self,
        hospital_id: UUID,
    ) -> None:
        """
        Ensure the specified Hospital exists.
        """

        hospital = (
            self.hospital_repository.get_hospital_by_id(
                hospital_id,
            )
        )

        if hospital is None:
            raise HospitalNotFoundError(
                f"Hospital '{hospital_id}' does not exist.",
            )

    def _validate_create_dates(
        self,
        data: StaffCreate,
    ) -> None:
        """
        Validate employment dates supplied during Staff creation.

        StaffCreate contains employment information because creation
        creates the initial StaffEmployment record.
        """

        if (
            data.date_of_birth is not None
            and data.date_employed < data.date_of_birth
        ):
            raise InvalidEmploymentDateError(
                "Employment date cannot be before date of birth.",
            )

        if (
            data.date_left is not None
            and data.date_left < data.date_employed
        ):
            raise InvalidEmploymentDateError(
                "Date left cannot be before employment date.",
            )

        if (
            data.date_left is not None
            and data.date_of_birth is not None
            and data.date_left < data.date_of_birth
        ):
            raise InvalidEmploymentDateError(
                "Date left cannot be before date of birth.",
            )

    # =========================================================================
    # Factory Helpers
    # =========================================================================

    @staticmethod
    def _build_staff(
        data: StaffCreate,
    ) -> Staff:
        """
        Create a Staff ORM object.

        Employment information is stored separately in
        StaffEmployment.
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
        )