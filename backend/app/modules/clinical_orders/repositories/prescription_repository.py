"""
==============================================================================
LIGHTBURGH EMR

Prescription Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clinical_orders.models import Prescription


class PrescriptionRepository:
    """
    Persistence operations for structured prescriptions.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        *,
        prescription: Prescription,
    ) -> Prescription:
        self.db.add(prescription)
        return prescription

    def get_by_id(
        self,
        *,
        prescription_id: UUID,
    ) -> Prescription | None:
        statement = select(Prescription).where(
            Prescription.id == prescription_id,
        )

        return self.db.scalar(statement)

    def get_by_order_id(
        self,
        *,
        order_id: UUID,
    ) -> Prescription | None:
        statement = select(Prescription).where(
            Prescription.clinical_order_id == order_id,
        )

        return self.db.scalar(statement)
