"""
==============================================================================
LIGHTBURGH EMR

Medication Administration Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.clinical_orders.models import (
    MedicationAdministration,
    MedicationDose,
)


class MedicationAdministrationRepository:
    """
    Persistence operations for medication administrations.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_by_dose_id(
        self,
        *,
        dose_id: UUID,
    ) -> MedicationAdministration | None:
        statement = (
            select(MedicationAdministration)
            .where(
                MedicationAdministration.dose_id == dose_id,
            )
        )

        return self.db.scalar(statement)

    def get_dose(
        self,
        *,
        dose_id: UUID,
    ) -> MedicationDose | None:
        statement = (
            select(MedicationDose)
            .options(
                selectinload(
                    MedicationDose.treatment,
                ),
                selectinload(
                    MedicationDose.administration,
                ),
            )
            .where(
                MedicationDose.id == dose_id,
            )
        )

        return self.db.scalar(statement)

    def create(
        self,
        *,
        administration: MedicationAdministration,
    ) -> MedicationAdministration:
        self.db.add(administration)
        return administration

    def flush(self) -> None:
        self.db.flush()
