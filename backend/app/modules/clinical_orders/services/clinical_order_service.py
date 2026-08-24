"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Service
==============================================================================

Business logic for Clinical Orders.

Clinical Orders represent requests for work that must be fulfilled by
another clinical workflow.

Hierarchy:

    Clinical Order
        -> Encounter
            -> Episode
                -> Hospital
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import (
    ClinicalOrderStatus,
    ClinicalOrderType,
)
from app.modules.clinical_orders.exceptions import (
    ClinicalOrderAlreadyCancelledError,
    ClinicalOrderAlreadyCompletedError,
    ClinicalOrderEncounterClosedError,
    ClinicalOrderEpisodeCancelledError,
    ClinicalOrderEpisodeClosedError,
    ClinicalOrderNotFoundError,
    ClinicalOrderStaffHospitalMismatchError,
    ClinicalOrderStaffNotFoundError,
)
from app.modules.clinical_orders.models import ClinicalOrder
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.encounter.exceptions import (
    EncounterAlreadyClosedError,
    EncounterNotFoundError,
)
from app.modules.encounter.models import EncounterStatus
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.exceptions import (
    EpisodeAlreadyClosedError,
    EpisodeAlreadyCancelledError,
    EpisodeNotFoundError,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.staff.repository import StaffRepository

class ClinicalOrderService:
    """
    Business logic for Clinical Orders.
    """

    def __init__(
        self,
        *,
        repository: ClinicalOrderRepository,
        event_service: ClinicalEventService,
        encounter_repository: EncounterRepository,
        episode_repository: EpisodeRepository,
        staff_repository: StaffRepository,
    ) -> None:
        self.repository = repository
        self.event_service = event_service
        self.encounter_repository = encounter_repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _get_encounter(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ):
        encounter = self.encounter_repository.get_by_id(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError(
                "Encounter not found.",
            )

        return encounter

    def _get_episode(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ):
        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )

        if episode is None:
            raise EpisodeNotFoundError(
                "Episode not found.",
            )

        return episode

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        staff = self.staff_repository.get_by_user_account_id(
            hospital_id=context.hospital_id,
            user_account_id=context.user_id,
        )

        if staff is None:
            raise ClinicalOrderStaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise ClinicalOrderStaffHospitalMismatchError(
                "Staff member belongs to another hospital.",
            )

        return staff

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_order(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
        order_type: ClinicalOrderType,
        priority: str,
        details: dict,
    ) -> ClinicalOrder:
        """
        Create a Clinical Order and its corresponding Clinical Event
        atomically.
        """

        if not isinstance(order_type, ClinicalOrderType):
            raise ValueError(
                "Invalid clinical order type.",
            )

        encounter = self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        if encounter.status != EncounterStatus.OPEN:
            raise ClinicalOrderEncounterClosedError(
                "Clinical Orders cannot be created on a closed Encounter.",
            )

        episode = self._get_episode(
            context=context,
            episode_id=encounter.episode_id,
        )

        if episode.status == EpisodeStatus.CLOSED:
            raise ClinicalOrderEpisodeClosedError()

        if episode.status == EpisodeStatus.CANCELLED:
            raise ClinicalOrderEpisodeCancelledError()

        if episode.status not in (
            EpisodeStatus.OPEN,
            EpisodeStatus.ADMITTED,
        ):
            raise EpisodeNotFoundError(
                "Episode is not available for Clinical Orders.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        ordered_at = datetime.now(UTC)

        order = ClinicalOrder(
            encounter_id=encounter.id,
            ordered_by=staff.id,
            order_type=order_type,
            status=ClinicalOrderStatus.REQUESTED,
            priority=priority,
            details=details,
            ordered_at=ordered_at,
            started_at=None,
            completed_at=None,
            cancelled_at=None,
        )

        try:
            self.repository.create(
                order=order,
            )

            self.repository.db.flush()

            event_type = {
                ClinicalOrderType.LABORATORY: EventType.INVESTIGATION_ORDERED,
                ClinicalOrderType.RADIOLOGY: EventType.INVESTIGATION_ORDERED,
                ClinicalOrderType.MEDICATION: EventType.MEDICATION_PRESCRIBED,
            }[order_type]

            self.event_service.create_event(
                context=context,
                encounter_id=encounter.id,
                event_type=event_type,
                performed_by=staff.id,
                occurred_at=ordered_at,
                payload={
                    "clinical_order_id": str(order.id),
                    "order_type": order_type.value,
                    "priority": priority,
                    "details": details,
                },
                commit=False,
            )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(order)

        return order

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> ClinicalOrder:
        order = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

        if order is None:
            raise ClinicalOrderNotFoundError(
                "Clinical Order not found.",
            )

        return order

    # ------------------------------------------------------------------
    # List Encounter Orders
    # ------------------------------------------------------------------

    def list_encounter_orders(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> list[ClinicalOrder]:
        encounter = self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        return self.repository.list_by_encounter(
            hospital_id=context.hospital_id,
            encounter_id=encounter.id,
        )

    # ------------------------------------------------------------------
    # Cancel
    # ------------------------------------------------------------------

    def cancel_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> ClinicalOrder:
        order = self.get_order(
            context=context,
            order_id=order_id,
        )

        if order.status == ClinicalOrderStatus.COMPLETED:
            raise ClinicalOrderAlreadyCompletedError(
                "Completed Clinical Orders cannot be cancelled.",
            )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise ClinicalOrderAlreadyCancelledError(
                "Clinical Order is already cancelled.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        cancelled_at = datetime.now(UTC)

        order.status = ClinicalOrderStatus.CANCELLED
        order.cancelled_at = cancelled_at

        try:
            self.repository.db.flush()

            self.event_service.create_event(
                context=context,
                encounter_id=order.encounter_id,
                event_type=EventType.CLINICAL_ORDER_CANCELLED,
                performed_by=staff.id,
                occurred_at=cancelled_at,
                payload={
                    "clinical_order_id": str(order.id),
                    "action": "CANCELLED",
                    "order_type": order.order_type.value,
                },
                commit=False,
            )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(order)

        return order
