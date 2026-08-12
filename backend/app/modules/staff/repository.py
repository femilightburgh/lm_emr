"""
==============================================================================
LIGHTBURGH EMR

Staff Repository

==============================================================================

Purpose
-------
Provides data access operations for the Staff entity.

The repository is responsible only for persistence and retrieval of Staff
records. It contains no business rules or application logic.

Business decisions belong in the StaffService.

==============================================================================
"""

from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Staff


class StaffRepository:
    """
    Repository for Staff persistence operations.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository.

        Parameters
        ----------
        session:
            Active SQLAlchemy database session.
        """
        self.session = session

    def create(
        self,
        staff: Staff,
    ) -> Staff:
        """
        Add a new Staff entity to the current transaction.

        The caller is responsible for committing the transaction.
        """

        self.session.add(staff)
        return staff

    def get_by_id(
        self,
        staff_id: UUID,
        ) -> Staff | None:
        """
        Retrieve a staff member by its unique identifier.

        Parameters
        ----------
        staff_id:
            Unique identifier of the staff member.

        Returns
        -------
        Staff | None
            The matching Staff entity if found; otherwise None.
        """

        statement = select(Staff).where(
            Staff.id == staff_id,
        )

        return self.session.scalar(statement)

    def get_by_staff_number(
        self,
        hospital_id: UUID,
        staff_number: str,
        ) -> Staff | None:
        """
        Retrieve a staff member by hospital and staff number.

        Parameters
        ----------
        hospital_id:
            Identifier of the hospital.

        staff_number:
            Staff number assigned within the hospital.

        Returns
        -------
        Staff | None
            Matching staff member if found; otherwise None.
        """

        statement = (
            select(Staff)
            .where(Staff.hospital_id == hospital_id)
            .where(Staff.staff_number == staff_number)
        )

        return self.session.scalar(statement)

    def list_staff(
        self,
        hospital_id: UUID,
        ) -> list[Staff]:
        """
        Retrieve all staff members belonging to a hospital.
        """

        statement = (
            select(Staff)
            .where(Staff.hospital_id == hospital_id)
            .order_by(
                Staff.last_name,
                Staff.first_name,
            )
        )

        return list(
            self.session.scalars(statement)
        )

    def save(self, staff: Staff) -> Staff:
        """
        Persist changes to an existing Staff entity.

        The caller is responsible for committing the transaction.
        """

        self.session.flush()
        self.session.refresh(staff)

        return staff


    def commit(self) -> None:
        """
        Commit the current database transaction.
        """

        self.session.commit()


    def refresh(self, staff: Staff) -> Staff:
        """
        Refresh a Staff entity from the database.
        """

        self.session.refresh(staff)
        return staff

    def flush(self) -> None:
        """
        Flush pending changes without committing the transaction.
        """
        self.session.flush()