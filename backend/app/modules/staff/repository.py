"""
==============================================================================
LIGHTBURGH EMR

Staff Repository

==============================================================================

Purpose
-------
Provides data access operations for Staff and StaffEmployment entities.

The repository is responsible only for persistence and retrieval.

Business decisions belong in services.

==============================================================================
"""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Staff, StaffEmployment


class StaffRepository:
    """
    Repository for Staff persistence operations.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        """
        Initialize the repository.

        Parameters
        ----------
        session:
            Active SQLAlchemy database session.
        """

        self.session = session

    # =========================================================================
    # Create
    # =========================================================================

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

    # =========================================================================
    # Retrieve Staff
    # =========================================================================

    def get_by_id(
        self,
        staff_id: UUID,
    ) -> Staff | None:
        """
        Retrieve a Staff member by its unique identifier.
        """

        statement = (
            select(Staff)
            .where(
                Staff.id == staff_id,
            )
        )

        return self.session.scalar(
            statement,
        )

    def get_by_staff_number(
        self,
        hospital_id: UUID,
        staff_number: str,
    ) -> Staff | None:
        """
        Retrieve a Staff member by hospital and staff number.
        """

        statement = (
            select(Staff)
            .where(
                Staff.hospital_id == hospital_id,
                Staff.staff_number == staff_number,
            )
        )

        return self.session.scalar(
            statement,
        )

    def list_staff(
        self,
        hospital_id: UUID,
    ) -> list[Staff]:
        """
        Retrieve all Staff members belonging to a Hospital.
        """

        statement = (
            select(Staff)
            .where(
                Staff.hospital_id == hospital_id,
            )
            .order_by(
                Staff.last_name,
                Staff.first_name,
            )
        )

        return list(
            self.session.scalars(
                statement,
            )
        )


    def get_by_user_account_id(
        self,
        hospital_id: UUID,
        user_account_id: UUID,
    ) -> Staff | None:
        """
        Retrieve a Staff member associated with a UserAccount
        within a specific Hospital.
        """

        statement = (
            select(Staff)
            .where(
                Staff.hospital_id == hospital_id,
                Staff.user_account_id == user_account_id,
            )
        )

        return self.session.scalar(
            statement,
        )

    # =========================================================================
    # Employment
    # =========================================================================

    def get_active_employment(
        self,
        staff_id: UUID,
        *,
        as_of: date | None = None,
    ) -> StaffEmployment | None:
        """
        Retrieve the active employment period for a Staff member.

        An employment is considered active when:

            date_employed <= as_of

        and:

            date_left IS NULL

        If ``as_of`` is not supplied, today's date is used.

        Employment history is retained, so this method deliberately
        selects the employment period that is active at the requested
        point in time rather than assuming the first or last employment
        record is current.
        """

        if as_of is None:
            as_of = date.today()

        statement = (
            select(StaffEmployment)
            .where(
                StaffEmployment.staff_id == staff_id,
                StaffEmployment.date_employed <= as_of,
                StaffEmployment.date_left.is_(None),
            )
            .order_by(
                StaffEmployment.date_employed.desc(),
            )
            .limit(1)
        )

        return self.session.scalar(
            statement,
        )

    # =========================================================================
    # Persistence
    # =========================================================================

    def save(
        self,
        staff: Staff,
    ) -> Staff:
        """
        Persist changes to an existing Staff entity.

        The caller is responsible for committing the transaction.
        """

        self.session.flush()
        self.session.refresh(
            staff,
        )

        return staff

    def commit(self) -> None:
        """
        Commit the current database transaction.
        """

        self.session.commit()

    def refresh(
        self,
        staff: Staff,
    ) -> Staff:
        """
        Refresh a Staff entity from the database.
        """

        self.session.refresh(
            staff,
        )

        return staff

    def flush(self) -> None:
        """
        Flush pending changes without committing the transaction.
        """

        self.session.flush()