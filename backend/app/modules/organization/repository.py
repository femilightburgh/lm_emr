"""
==============================================================================
LIGHTBURGH EMR

Organization Repository

==============================================================================

Repository layer for Organization module.

Responsibilities
----------------
• Retrieve hospitals
• Persist hospitals
• Manage database transactions

Business rules belong in the service layer.

==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.organization.models import Hospital


class OrganizationRepository:
    """
    Repository for organization-related read operations.
    """

    def __init__(self, db: Session):
        self.db = db


class HospitalRepository:
    """
    Repository responsible for Hospital persistence and retrieval.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Query Operations
    # ------------------------------------------------------------------

    def get_hospital_by_id(
        self,
        hospital_id: UUID,
    ) -> Hospital | None:
        """
        Retrieve a hospital using its primary key.
        """

        statement = (
            select(Hospital)
            .where(Hospital.id == hospital_id)
        )

        return self.db.scalar(statement)

    def get_hospital_by_code(
        self,
        code: str,
    ) -> Hospital | None:
        """
        Retrieve a hospital using its unique code.
        """

        statement = (
            select(Hospital)
            .where(Hospital.code == code)
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # Persistence Operations
    # ------------------------------------------------------------------

    def create_hospital(
        self,
        hospital: Hospital,
    ) -> Hospital:
        """
        Add a new hospital to the current transaction.

        The service layer is responsible for committing
        the transaction.
        """

        self.db.add(hospital)
        return hospital

    # ------------------------------------------------------------------
    # Transaction Operations
    # ------------------------------------------------------------------

    def flush(self) -> None:
        """
        Flush pending changes to the database without committing.
        """

        self.db.flush()

    def save(self) -> None:
        """
        Commit all pending database changes.
        """

        self.db.commit()

    def refresh(
        self,
        entity,
    ) -> None:
        """
        Reload an entity from the database.
        """

        self.db.refresh(entity)

    def rollback(self) -> None:
        """
       Roll back the current transaction.
        """

        self.db.rollback()