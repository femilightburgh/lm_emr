"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clinical_orders.models import ClinicalOrder
from app.modules.encounter.models import Encounter
from app.modules.episode.models import Episode


class ClinicalOrderRepository:
    """
    Persistence operations for Clinical Orders.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        order: ClinicalOrder,
    ) -> ClinicalOrder:
        self.db.add(order)
        return order

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        order_id: UUID,
    ) -> ClinicalOrder | None:
        statement = (
            select(ClinicalOrder)
            .join(
                Encounter,
                ClinicalOrder.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalOrder.id == order_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # Encounter Orders
    # ------------------------------------------------------------------

    def list_by_encounter(
        self,
        *,
        hospital_id: UUID,
        encounter_id: UUID,
    ) -> list[ClinicalOrder]:
        statement = (
            select(ClinicalOrder)
            .join(
                Encounter,
                ClinicalOrder.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalOrder.encounter_id == encounter_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalOrder.ordered_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        self.db.commit()

    def refresh(
        self,
        order: ClinicalOrder,
    ) -> None:
        self.db.refresh(order)
