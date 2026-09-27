"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.clinical_orders.models import (
    ClinicalOrder,
    ClinicalOrderItem,
)
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
            .options(
                selectinload(ClinicalOrder.items),
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
                ClinicalOrder.id == order_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)


    def get_by_item_id(
        self,
        *,
        hospital_id: UUID,
        order_item_id: UUID,
    ) -> ClinicalOrder | None:
        statement = (
            select(ClinicalOrder)
            .options(
                selectinload(ClinicalOrder.items),
            )
            .join(
                ClinicalOrderItem,
                ClinicalOrderItem.clinical_order_id
                == ClinicalOrder.id,
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
                ClinicalOrderItem.id == order_item_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # ------------------------------------------------------------------
    # Encounter Orders
    # ------------------------------------------------------------------

    def list_by_episode(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return all Clinical Orders belonging to an Episode.

        Clinical Orders remain attached to the Encounter in which
        they were created, but an Episode-level view is required
        by downstream clinical workflows such as Doctor Review.
        """

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
                Episode.id == episode_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalOrder.ordered_at.asc(),
            )
        )

        return list(self.db.scalars(statement))


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
    # Laboratory Queue
    # ------------------------------------------------------------------

    def list_laboratory_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return open laboratory orders requiring laboratory attention.

        Includes:
            REQUESTED
            IN_PROGRESS

        Only laboratory orders belonging to the authenticated
        Hospital are returned.
        """

        from app.modules.clinical_orders.enums import (
            ClinicalOrderStatus,
            ClinicalOrderType,
        )

        statement = (
            select(ClinicalOrder)
            .options(
                selectinload(ClinicalOrder.items),
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
                Episode.hospital_id == hospital_id,
                ClinicalOrder.order_type
                == ClinicalOrderType.LABORATORY,
                ClinicalOrder.status.in_(
                    (
                        ClinicalOrderStatus.REQUESTED,
                        ClinicalOrderStatus.RECEIVED,
                        ClinicalOrderStatus.IN_PROGRESS,
                    ),
                ),
            )
            .order_by(
                ClinicalOrder.ordered_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Diagnostics Queue
    # ------------------------------------------------------------------

    def list_diagnostic_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return open diagnostic orders requiring attention.

        Includes:

            REQUESTED
            RECEIVED
            IN_PROGRESS
        """

        from app.modules.clinical_orders.enums import (
            ClinicalOrderStatus,
            ClinicalOrderType,
        )

        statement = (
            select(ClinicalOrder)
            .options(
                selectinload(ClinicalOrder.items),
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
                Episode.hospital_id == hospital_id,
                ClinicalOrder.order_type.in_(
                    (
                        ClinicalOrderType.DIAGNOSTIC,
                        ClinicalOrderType.RADIOLOGY,
                    ),
                ),
                ClinicalOrder.status.in_(
                    (
                        ClinicalOrderStatus.REQUESTED,
                        ClinicalOrderStatus.RECEIVED,
                        ClinicalOrderStatus.IN_PROGRESS,
                    ),
                ),
            )
            .order_by(
                ClinicalOrder.ordered_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Pharmacy Queue
    # ------------------------------------------------------------------

    def list_pharmacy_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return open medication orders requiring pharmacy attention.

        Includes:
            REQUESTED
            RECEIVED
            IN_PROGRESS

        Only medication orders belonging to the authenticated
        Hospital are returned.
        """

        from app.modules.clinical_orders.enums import (
            ClinicalOrderStatus,
            ClinicalOrderType,
        )

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
                Episode.hospital_id == hospital_id,
                ClinicalOrder.order_type
                == ClinicalOrderType.MEDICATION,
                ClinicalOrder.status.in_(
                    (
                        ClinicalOrderStatus.REQUESTED,
                        ClinicalOrderStatus.RECEIVED,
                        ClinicalOrderStatus.IN_PROGRESS,
                    ),
                ),
            )
            .order_by(
                ClinicalOrder.ordered_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Episode Outstanding Investigations
    # ------------------------------------------------------------------

    def list_outstanding_investigation_orders_for_episode(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return outstanding laboratory/radiology orders for an Episode.

        REQUESTED, RECEIVED, and IN_PROGRESS investigation orders are
        considered outstanding. COMPLETED and CANCELLED orders are terminal.
        """

        from app.modules.clinical_orders.enums import (
            ClinicalOrderStatus,
            ClinicalOrderType,
        )

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
                Episode.id == episode_id,
                Episode.hospital_id == hospital_id,
                ClinicalOrder.order_type.in_(
                    (
                        ClinicalOrderType.LABORATORY,
                        ClinicalOrderType.RADIOLOGY,
                        ClinicalOrderType.DIAGNOSTIC,
                    ),
                ),
                ClinicalOrder.status.in_(
                    (
                        ClinicalOrderStatus.REQUESTED,
                        ClinicalOrderStatus.RECEIVED,
                        ClinicalOrderStatus.IN_PROGRESS,
                    ),
                ),
            )
            .order_by(
                ClinicalOrder.ordered_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # ------------------------------------------------------------------
    # Episode Outstanding Medication Orders
    # ------------------------------------------------------------------

    def list_outstanding_medication_orders_for_episode(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return outstanding medication orders for an Episode.

        REQUESTED, RECEIVED, and IN_PROGRESS medication orders are
        considered outstanding. COMPLETED and CANCELLED orders are
        terminal.
        """

        from app.modules.clinical_orders.enums import (
            ClinicalOrderStatus,
            ClinicalOrderType,
        )

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
                Episode.id == episode_id,
                Episode.hospital_id == hospital_id,
                ClinicalOrder.order_type
                == ClinicalOrderType.MEDICATION,
                ClinicalOrder.status.in_(
                    (
                        ClinicalOrderStatus.REQUESTED,
                        ClinicalOrderStatus.RECEIVED,
                        ClinicalOrderStatus.IN_PROGRESS,
                    ),
                ),
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
