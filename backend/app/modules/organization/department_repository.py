"""
LIGHTBURGH EMR

Department Repository

===============================================================================

Repository layer for hospital department persistence and retrieval.

Business rules belong in DepartmentService.

===============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.organization.models import Department


class DepartmentRepository:
    """
    Repository responsible for Department persistence and retrieval.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Query Operations
    # ------------------------------------------------------------------

    def get_by_id(
        self,
        department_id: UUID,
    ) -> Department | None:
        """
        Retrieve a department by its primary key.
        """

        statement = (
            select(Department)
            .where(Department.id == department_id)
        )

        return self.db.scalar(statement)

    def get_by_code(
        self,
        hospital_id: UUID,
        code: str,
    ) -> Department | None:
        """
        Retrieve a department by hospital and department code.
        """

        statement = (
            select(Department)
            .where(
                Department.hospital_id == hospital_id,
                Department.code == code,
            )
        )

        return self.db.scalar(statement)

    def list_by_hospital(
        self,
        hospital_id: UUID,
    ) -> list[Department]:
        """
        Retrieve all departments belonging to a hospital.

        Departments are ordered alphabetically by name.
        """

        statement = (
            select(Department)
            .where(Department.hospital_id == hospital_id)
            .order_by(Department.name)
        )

        return list(self.db.scalars(statement))

    # ------------------------------------------------------------------
    # Persistence Operations
    # ------------------------------------------------------------------

    def create(
        self,
        department: Department,
    ) -> Department:
        """
        Add a department to the current transaction.

        The service layer is responsible for committing.
        """

        self.db.add(department)
        return department

    # ------------------------------------------------------------------
    # Transaction Operations
    # ------------------------------------------------------------------

    def flush(self) -> None:
        """
        Flush pending changes without committing.
        """

        self.db.flush()

    def save(self) -> None:
        """
        Commit the current transaction.
        """

        self.db.commit()

    def delete(
        self,
        department: Department,
    ) -> None:
        """
        Delete a department from the current transaction.

        The caller is responsible for committing the transaction.
        """

        self.db.delete(department)

    def refresh(
        self,
        department: Department,
    ) -> None:
        """
        Refresh a department from the database.
        """

        self.db.refresh(department)

    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """

        self.db.rollback()