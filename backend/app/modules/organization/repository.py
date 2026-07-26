"""
========================================================================

LIGHTBURGH EMR

Organization Repository

========================================================================

Repository Responsibilities
---------------------------

Provides database access for Organization-related entities.

Business rules should NOT exist here.

========================================================================
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.organization.models import Hospital
from uuid import UUID

class OrganizationRepository:
    """
    Repository responsible for Organization-related
    database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_hospital_by_code(
        self,
        code: str,
    ) -> Hospital | None:
        """
        Retrieve a hospital using its unique hospital code.
        """

        statement = (
            select(Hospital)
            .where(Hospital.code == code)
        )

        return self.db.scalar(statement)
    


class HospitalRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(
        self,
        hospital_id: UUID,
    ) -> Hospital | None:

        statement = (
            select(Hospital)
            .where(Hospital.id == hospital_id)
        )

        return self.session.scalar(statement)