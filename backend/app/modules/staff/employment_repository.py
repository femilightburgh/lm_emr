"""
LIGHTBURGH EMR

Staff Employment Repository

===============================================================================

Purpose
-------
Provides data access operations for StaffEmployment entities.

The repository is responsible only for persistence and retrieval.
Business rules such as employment lifecycle, re-employment, date validation,
and active-employment constraints belong in StaffService.

===============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import StaffEmployment


class StaffEmploymentRepository:
    """
    Repository for StaffEmployment persistence operations.
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
        employment: StaffEmployment,
    ) -> StaffEmployment:
        """
        Add a new employment record to the current transaction.

        The caller is responsible for committing the transaction.
        """

        self.session.add(employment)
        return employment

    def get_by_id(
        self,
        employment_id: UUID,
    ) -> StaffEmployment | None:
        """
        Retrieve an employment record by its unique identifier.
        """

        statement = select(StaffEmployment).where(
            StaffEmployment.id == employment_id,
        )

        return self.session.scalar(statement)

    def get_current(
        self,
        staff_id: UUID,
    ) -> StaffEmployment | None:
        """
        Retrieve the current active employment record for a staff member.
        """

        statement = (
            select(StaffEmployment)
            .where(
                StaffEmployment.staff_id == staff_id,
                StaffEmployment.date_left.is_(None),
            )
            .order_by(
                StaffEmployment.date_employed.desc(),
            )
        )

        return self.session.scalar(statement)

    def list_by_staff(
        self,
        staff_id: UUID,
    ) -> list[StaffEmployment]:
        """
        Retrieve the complete employment history for a staff member.

        Results are ordered from most recent employment period
        to oldest.
        """

        statement = (
            select(StaffEmployment)
            .where(
                StaffEmployment.staff_id == staff_id,
            )
            .order_by(
                StaffEmployment.date_employed.desc(),
            )
        )

        return list(
            self.session.scalars(statement)
        )

    def save(
        self,
        employment: StaffEmployment,
    ) -> StaffEmployment:
        """
        Persist changes to an existing employment record.

        The caller is responsible for transaction-level business logic.
        """

        self.session.flush()
        self.session.refresh(employment)

        return employment