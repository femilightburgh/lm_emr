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

    def create(self, staff: Staff) -> Staff:
        """
        Persist a new staff member.

        Parameters
        ----------
        staff:
            The Staff entity to persist.

        Returns
        -------
        Staff
            The persisted Staff entity with generated fields populated.
        """

        self.session.add(staff)
        self.session.commit()
        self.session.refresh(staff)

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
        Persist changes made to an existing staff member.
        """

        try:
            self.session.commit()
            self.session.refresh(staff)
            return staff

        except Exception:
            self.session.rollback()
            raise