"""
==============================================================================
LIGHTBURGH EMR

Inpatient Medication Treatment Repository
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.clinical_orders.models import (
    MedicationDose,
    MedicationTreatment,
    MedicationTreatmentStatus,
)


class MedicationTreatmentRepository:
    """
    Persistence operations for inpatient medication treatments.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        *,
        treatment: MedicationTreatment,
    ) -> MedicationTreatment:
        self.db.add(treatment)
        return treatment

    def get_by_id(
        self,
        *,
        treatment_id: UUID,
    ) -> MedicationTreatment | None:
        statement = (
            select(MedicationTreatment)
            .options(
                selectinload(
                    MedicationTreatment.prescription,
                ),
                selectinload(
                    MedicationTreatment.episode,
                ),
                selectinload(
                    MedicationTreatment.doses,
                ).selectinload(
                    MedicationDose.administration,
                ),
            )
            .where(
                MedicationTreatment.id
                == treatment_id,
            )
        )

        return self.db.scalar(statement)

    def get_by_prescription_id(
        self,
        *,
        prescription_id: UUID,
    ) -> MedicationTreatment | None:
        statement = (
            select(MedicationTreatment)
            .options(
                selectinload(
                    MedicationTreatment.prescription,
                ),
                selectinload(
                    MedicationTreatment.doses,
                ).selectinload(
                    MedicationDose.administration,
                ),
            )
            .where(
                MedicationTreatment.prescription_id
                == prescription_id,
            )
        )

        return self.db.scalar(statement)

    def list_active_by_episode(
        self,
        *,
        episode_id: UUID,
    ) -> list[MedicationTreatment]:
        statement = (
            select(MedicationTreatment)
            .options(
                selectinload(
                    MedicationTreatment.prescription,
                ),
                selectinload(
                    MedicationTreatment.doses,
                ).selectinload(
                    MedicationDose.administration,
                ),
            )
            .where(
                MedicationTreatment.episode_id
                == episode_id,
                MedicationTreatment.status
                == MedicationTreatmentStatus.ACTIVE,
            )
            .order_by(
                MedicationTreatment.start_at,
            )
        )

        return list(
            self.db.scalars(statement).all(),
        )

    def list_doses_for_episode(
        self,
        *,
        episode_id: UUID,
        from_time: datetime,
        to_time: datetime,
    ) -> list[MedicationDose]:
        statement = (
            select(MedicationDose)
            .join(
                MedicationDose.treatment,
            )
            .options(
                selectinload(
                    MedicationDose.treatment,
                ).selectinload(
                    MedicationTreatment.prescription,
                ),
                selectinload(
                    MedicationDose.administration,
                ),
            )
            .where(
                MedicationTreatment.episode_id
                == episode_id,
                MedicationTreatment.status
                == MedicationTreatmentStatus.ACTIVE,
                MedicationDose.scheduled_at
                >= from_time,
                MedicationDose.scheduled_at
                <= to_time,
            )
            .order_by(
                MedicationDose.scheduled_at,
            )
        )

        return list(
            self.db.scalars(statement).all(),
        )


    def list_due_doses(
        self,
        *,
        episode_id: UUID,
        from_time: datetime,
        to_time: datetime,
    ) -> list[MedicationDose]:
        statement = (
            select(MedicationDose)
            .join(
                MedicationDose.treatment,
            )
            .options(
                selectinload(
                    MedicationDose.treatment,
                ).selectinload(
                    MedicationTreatment.prescription,
                ),
                selectinload(
                    MedicationDose.administration,
                ),
            )
            .where(
                MedicationTreatment.episode_id
                == episode_id,
                MedicationTreatment.status
                == MedicationTreatmentStatus.ACTIVE,
                MedicationDose.scheduled_at
                >= from_time,
                MedicationDose.scheduled_at
                <= to_time,
            )
            .order_by(
                MedicationDose.scheduled_at,
            )
        )

        return list(
            self.db.scalars(statement).all(),
        )

    def flush(self) -> None:
        self.db.flush()

    def refresh(
        self,
        treatment: MedicationTreatment,
    ) -> None:
        self.db.refresh(treatment)
