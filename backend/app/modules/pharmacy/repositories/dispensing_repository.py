"""
==============================================================================
LIGHTBURGH EMR

Dispensing Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.pharmacy.models import Dispensing


class DispensingRepository:
    """
    Persistence operations for medication dispensing records.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        *,
        dispensing: Dispensing,
    ) -> Dispensing:
        self.db.add(dispensing)
        return dispensing

    def get_by_prescription_id(
        self,
        *,
        prescription_id: UUID,
    ) -> Dispensing | None:
        statement = select(Dispensing).where(
            Dispensing.prescription_id == prescription_id,
        )

        return self.db.scalar(statement)
