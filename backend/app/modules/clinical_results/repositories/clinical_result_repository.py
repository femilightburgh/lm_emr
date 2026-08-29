"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.clinical_orders.models import ClinicalOrder
from app.modules.clinical_results.models import (
    ClinicalResult,
    ClinicalResultValue,
)
from app.modules.encounter.models import Encounter
from app.modules.episode.models import Episode


class ClinicalResultRepository:
    """
    Persistence operations for Clinical Results.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        *,
        result: ClinicalResult,
    ) -> ClinicalResult:
        self.db.add(result)
        return result

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        result_id: UUID,
    ) -> ClinicalResult | None:
        statement = (
            select(ClinicalResult)
            .options(
                selectinload(
                    ClinicalResult.values,
                ).selectinload(
                    ClinicalResultValue.analyte,
                ),
            )
            .join(
                ClinicalOrder,
                ClinicalResult.order_id == ClinicalOrder.id,
            )
            .join(
                Encounter,
                ClinicalOrder.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalResult.id == result_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    def list_by_order(
        self,
        *,
        hospital_id: UUID,
        order_id: UUID,
    ) -> list[ClinicalResult]:
        statement = (
            select(ClinicalResult)
            .options(
                selectinload(
                    ClinicalResult.values,
                ).selectinload(
                    ClinicalResultValue.analyte,
                ),
            )
            .join(
                ClinicalOrder,
                ClinicalResult.order_id == ClinicalOrder.id,
            )
            .join(
                Encounter,
                ClinicalOrder.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalResult.order_id == order_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalResult.recorded_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    def delete_values(
        self,
        *,
        result: ClinicalResult,
    ) -> None:
        for value in list(result.values):
            self.db.delete(value)

    def save(self) -> None:
        self.db.commit()

    def refresh(
        self,
        result: ClinicalResult,
    ) -> None:
        self.db.refresh(result)
