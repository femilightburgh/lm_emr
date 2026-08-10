"""
LIGHTBURGH EMR

Department Service

===============================================================================

Business logic for hospital department management.

Departments belong to a specific hospital and are retained historically.
Inactive departments cannot be used for new staff assignments.

===============================================================================
"""

from uuid import UUID

from app.common.exceptions import DuplicateResourceException
from app.modules.organization.department_repository import DepartmentRepository
from app.modules.organization.enums import DepartmentStatus
from app.modules.organization.models import Department
from app.modules.organization.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
)
from app.modules.organization.repository import HospitalRepository
from app.modules.organization.exceptions import (
    DepartmentInactiveError,
    DepartmentNotFoundError,
)


class DepartmentService:
    """
    Handles business logic for hospital departments.
    """

    def __init__(
        self,
        repository: DepartmentRepository,
        hospital_repository: HospitalRepository,
    ) -> None:
        self.repository = repository
        self.hospital_repository = hospital_repository

    def create_department(
        self,
        data: DepartmentCreate,
    ) -> Department:
        """
        Create a department within a hospital.

        The hospital must exist and the department code must be
        unique within that hospital.
        """

        hospital = self.hospital_repository.get_hospital_by_id(
            data.hospital_id,
        )

        if hospital is None:
            raise ValueError(
                f"Hospital '{data.hospital_id}' does not exist."
            )

        existing = self.repository.get_by_code(
            hospital_id=data.hospital_id,
            code=data.code,
        )

        if existing is not None:
            raise DuplicateResourceException(
                f"Department code '{data.code}' already exists "
                "within this hospital."
            )

        department = Department(
            hospital_id=data.hospital_id,
            name=data.name,
            code=data.code,
            category=data.category,
            status=data.status,
        )

        try:
            self.repository.create(department)
            self.repository.flush()
            self.repository.save()
            self.repository.refresh(department)

            return department

        except Exception:
            self.repository.rollback()
            raise

    def get_department(
        self,
        department_id: UUID,
    ) -> Department:
        """
        Retrieve a department by ID.
        """

        department = self.repository.get_by_id(department_id)

        if department is None:
            raise DepartmentNotFoundError(
                f"Department '{department_id}' does not exist."
            )

        return department

    def update_department(
        self,
        department_id: UUID,
        data: DepartmentUpdate,
    ) -> Department:
        """
        Update an existing department.

        Supports partial updates while preserving the department's
        hospital ownership.
        """

        department = self.get_department(department_id)

        updates = data.model_dump(
            exclude_unset=True,
        )

        if "code" in updates:
            existing = self.repository.get_by_code(
                hospital_id=department.hospital_id,
                code=updates["code"],
            )

            if (
                existing is not None
                and existing.id != department.id
            ):
                raise DuplicateResourceException(
                    f"Department code '{updates['code']}' already exists "
                    "within this hospital."
                )

        for field, value in updates.items():
            setattr(department, field, value)

        try:
            self.repository.save()
            self.repository.refresh(department)

            return department

        except Exception:
            self.repository.rollback()
            raise

    def delete_department(
        self,
        department_id: UUID,
    ) -> None:
        """
        Delete an existing department.

        The department must exist before deletion.
        """

        department = self.get_department(department_id)

        try:
            self.repository.delete(department)
            self.repository.save()

        except Exception:
            self.repository.rollback()
            raise

    def list_departments(
        self,
        hospital_id: UUID,
    ) -> list[Department]:
        """
        Retrieve all departments belonging to a hospital.
        """

        hospital = self.hospital_repository.get_hospital_by_id(
            hospital_id,
        )

        if hospital is None:
            raise ValueError(
                f"Hospital '{hospital_id}' does not exist."
            )

        return self.repository.list_by_hospital(hospital_id)

    def require_active(
        self,
        department_id: UUID,
    ) -> Department:
        """
        Retrieve a department and ensure it is active.

        Intended for operations that create new staff assignments.
        """

        department = self.get_department(department_id)

        if department.status != DepartmentStatus.ACTIVE:
            raise DepartmentInactiveError(
                f"Department '{department_id}' is inactive."
            )

        return department