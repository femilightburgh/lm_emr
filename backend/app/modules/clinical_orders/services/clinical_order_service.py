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
from app.modules.clinical_orders.models import (
    ClinicalOrder,
    ClinicalOrderItem,
    ClinicalOrderItemType,
    Prescription,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    PrescriptionRepository,
)
from app.modules.diagnostics.repositories.diagnostic_repository import (
    DiagnosticRepository,
)
from app.modules.laboratory.repositories.laboratory_test_repository import (
    LaboratoryTestRepository,
)
from app.modules.clinical_orders.services.medication_treatment_service import (
    InpatientMedicationService,
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
        prescription_repository: PrescriptionRepository,
        laboratory_test_repository: LaboratoryTestRepository,
        diagnostic_repository: DiagnosticRepository,
        inpatient_medication_service: InpatientMedicationService | None = None,
    ) -> None:
        self.repository = repository
        self.event_service = event_service
        self.encounter_repository = encounter_repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository
        self.prescription_repository = prescription_repository
        self.laboratory_test_repository = laboratory_test_repository
        self.diagnostic_repository = diagnostic_repository
        self.inpatient_medication_service = (
            inpatient_medication_service
        )

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
        items: list[dict] | None = None,
        start_at: datetime | None = None,
        first_dose_at: datetime | None = None,
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
            order_items = items or []

            if order_type == ClinicalOrderType.LABORATORY:
                if not order_items:
                    raise ValueError(
                        "Laboratory orders require at least one laboratory test."
                    )

            elif order_type == ClinicalOrderType.DIAGNOSTIC:
                if not order_items:
                    raise ValueError(
                        "Diagnostic orders require at least one investigation."
                    )

            elif order_type == ClinicalOrderType.MEDICATION:
                if order_items:
                    raise ValueError(
                        "Medication orders cannot contain investigation items."
                    )

            elif order_type == ClinicalOrderType.RADIOLOGY:
                if order_items:
                    raise ValueError(
                        "Radiology orders do not support investigation items yet."
                    )

            clinical_order_items: list[ClinicalOrderItem] = []

            for display_order, item in enumerate(order_items):
                laboratory_test_id = item.get(
                    "laboratory_test_id",
                )
                diagnostic_investigation_id = item.get(
                    "diagnostic_investigation_id",
                )
                custom_name = item.get("custom_name")

                if isinstance(custom_name, str):
                    custom_name = custom_name.strip()
                    if not custom_name:
                        raise ValueError(
                            "Custom investigation name cannot be empty."
                        )
                elif custom_name is not None:
                    raise ValueError(
                        "Custom investigation name must be text."
                    )

                references = [
                    value is not None
                    for value in (
                        laboratory_test_id,
                        diagnostic_investigation_id,
                        custom_name,
                    )
                ]

                if sum(references) != 1:
                    raise ValueError(
                        "A Clinical Order item must reference exactly one "
                        "catalogue investigation or provide one custom "
                        "investigation name."
                    )

                if order_type == ClinicalOrderType.LABORATORY:
                    if diagnostic_investigation_id is not None:
                        raise ValueError(
                            "Laboratory orders can only contain laboratory tests."
                        )

                    if custom_name is not None:
                        clinical_order_items.append(
                            ClinicalOrderItem(
                                item_type=ClinicalOrderItemType.LABORATORY,
                                status=ClinicalOrderStatus.REQUESTED,
                                laboratory_test_id=None,
                                diagnostic_investigation_id=None,
                                display_order=display_order,
                                custom_name=custom_name,
                                details={
                                    "test_name": custom_name,
                                    "custom": True,
                                },
                            )
                        )
                        continue

                    laboratory_test = (
                        self.laboratory_test_repository.get_by_id(
                            hospital_id=context.hospital_id,
                            test_id=laboratory_test_id,
                        )
                    )

                    if laboratory_test is None:
                        raise ValueError(
                            "Laboratory test not found."
                        )

                    if any(
                        existing.laboratory_test_id
                        == laboratory_test.id
                        for existing in clinical_order_items
                    ):
                        raise ValueError(
                            "A laboratory test cannot be added twice "
                            "to the same Clinical Order."
                        )

                    clinical_order_items.append(
                        ClinicalOrderItem(
                            item_type=ClinicalOrderItemType.LABORATORY,
                            status=ClinicalOrderStatus.REQUESTED,
                            laboratory_test_id=laboratory_test.id,
                            diagnostic_investigation_id=None,
                            display_order=display_order,
                            details={
                                "test_code": laboratory_test.code,
                                "test_name": laboratory_test.name,
                            },
                        )
                    )

                elif order_type == ClinicalOrderType.DIAGNOSTIC:
                    if laboratory_test_id is not None:
                        raise ValueError(
                            "Diagnostic orders can only contain "
                            "diagnostic investigations."
                        )

                    if custom_name is not None:
                        clinical_order_items.append(
                            ClinicalOrderItem(
                                item_type=ClinicalOrderItemType.DIAGNOSTIC,
                                status=ClinicalOrderStatus.REQUESTED,
                                laboratory_test_id=None,
                                diagnostic_investigation_id=None,
                                display_order=display_order,
                                custom_name=custom_name,
                                details={
                                    "investigation_name": custom_name,
                                    "custom": True,
                                },
                            )
                        )
                        continue

                    investigation = self.diagnostic_repository.get_investigation(
                        hospital_id=context.hospital_id,
                        investigation_id=diagnostic_investigation_id,
                    )

                    if investigation is None:
                        raise ValueError(
                            "Diagnostic investigation not found."
                        )

                    if any(
                        existing.diagnostic_investigation_id
                        == investigation.id
                        for existing in clinical_order_items
                    ):
                        raise ValueError(
                            "A diagnostic investigation cannot be added twice "
                            "to the same Clinical Order."
                        )

                    clinical_order_items.append(
                        ClinicalOrderItem(
                            item_type=ClinicalOrderItemType.DIAGNOSTIC,
                            status=ClinicalOrderStatus.REQUESTED,
                            laboratory_test_id=None,
                            diagnostic_investigation_id=investigation.id,
                            display_order=display_order,
                            details={
                                "investigation_code": investigation.code,
                                "investigation_name": investigation.name,
                                "diagnostic_category": (
                                    investigation.category.value
                                ),
                            },
                        )
                    )

            if clinical_order_items:
                order.items.extend(clinical_order_items)

            self.repository.create(
                order=order,
            )

            self.repository.db.flush()

            if order_type == ClinicalOrderType.MEDICATION:
                prescription = Prescription(
                    clinical_order_id=order.id,
                    medicine_name=str(
                        details.get(
                            "medicine_name",
                            details.get(
                                "medication_id",
                                "",
                            ),
                        )
                    ).strip(),
                    strength=(
                        str(details["strength"]).strip()
                        if details.get("strength") is not None
                        else None
                    ),
                    dose=str(
                        details.get(
                            "dose",
                            "",
                        )
                    ).strip(),
                    dose_unit=(
                        str(details["dose_unit"]).strip()
                        if details.get("dose_unit") is not None
                        else None
                    ),
                    route=str(
                        details.get(
                            "route",
                            "",
                        )
                    ).strip(),
                    frequency=str(
                        details.get(
                            "frequency",
                            "",
                        )
                    ).strip(),
                    duration=(
                        str(details["duration"]).strip()
                        if details.get("duration") is not None
                        else None
                    ),
                    duration_unit=(
                        str(details["duration_unit"]).strip()
                        if details.get("duration_unit") is not None
                        else None
                    ),
                    quantity=(
                        str(details["quantity"]).strip()
                        if details.get("quantity") is not None
                        else None
                    ),
                    directions=(
                        str(details["directions"]).strip()
                        if details.get("directions") is not None
                        else None
                    ),
                    indication=(
                        str(details["indication"]).strip()
                        if details.get("indication") is not None
                        else None
                    ),
                )

                self.prescription_repository.create(
                    prescription=prescription,
                )

                self.repository.db.flush()

                if episode.status == EpisodeStatus.ADMITTED:
                    if self.inpatient_medication_service is None:
                        raise RuntimeError(
                            "Inpatient medication service is required "
                            "for admitted medication orders.",
                        )

                    self.inpatient_medication_service.create_treatment(
                        context=context,
                        prescription=prescription,
                        start_at=start_at,
                        first_dose_at=first_dose_at,
                    )

            event_type = {
                ClinicalOrderType.LABORATORY: EventType.INVESTIGATION_ORDERED,
                ClinicalOrderType.RADIOLOGY: EventType.INVESTIGATION_ORDERED,
                ClinicalOrderType.DIAGNOSTIC: EventType.INVESTIGATION_ORDERED,
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

    def _get_order_for_item(
        self,
        *,
        context: RequestContext,
        order_item_id: UUID,
    ) -> ClinicalOrder:
        """
        Retrieve the parent Clinical Order for an item while enforcing
        hospital isolation.
        """

        order = self.repository.get_by_item_id(
            hospital_id=context.hospital_id,
            order_item_id=order_item_id,
        )

        if order is None:
            from app.modules.clinical_orders.exceptions import (
                ClinicalOrderItemNotFoundError,
            )

            raise ClinicalOrderItemNotFoundError(
                "Clinical Order Item not found.",
            )

        return order


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
    # Laboratory Queue
    # ------------------------------------------------------------------

    def list_laboratory_queue(
        self,
        *,
        context: RequestContext,
    ) -> list[ClinicalOrder]:
        """
        Return laboratory orders requiring laboratory attention.
        """

        return self.repository.list_laboratory_queue(
            hospital_id=context.hospital_id,
        )


    # ------------------------------------------------------------------
    # Diagnostics Queue
    # ------------------------------------------------------------------

    def list_diagnostic_queue(
        self,
        *,
        context: RequestContext,
    ) -> list[ClinicalOrder]:
        """
        Return diagnostic orders requiring diagnostic attention.
        """

        return self.repository.list_diagnostic_queue(
            hospital_id=context.hospital_id,
        )

    # ------------------------------------------------------------------
    # Pharmacy Queue
    # ------------------------------------------------------------------

    def list_pharmacy_queue(
        self,
        *,
        context: RequestContext,
    ) -> list[ClinicalOrder]:
        """
        Return medication orders requiring pharmacy attention.
        """

        return self.repository.list_pharmacy_queue(
            hospital_id=context.hospital_id,
        )


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
    # List Episode Orders
    # ------------------------------------------------------------------

    def list_episode_orders(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> list[ClinicalOrder]:
        """
        Return all Clinical Orders belonging to an Episode.

        Orders remain owned by their original Encounter. This method
        provides an Episode-level clinical view for workflows such as
        Doctor Review, where investigation results from earlier
        encounters must remain visible.
        """

        episode = self._get_episode(
            context=context,
            episode_id=episode_id,
        )

        return self.repository.list_by_episode(
            hospital_id=context.hospital_id,
            episode_id=episode.id,
        )


    # ------------------------------------------------------------------
    # Receive
    # ------------------------------------------------------------------

    def receive_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> ClinicalOrder:
        """
        Move a Clinical Order from REQUESTED to RECEIVED.
        """

        from app.modules.clinical_orders.exceptions import (
            ClinicalOrderAlreadyReceivedError,
            ClinicalOrderCannotReceiveError,
        )

        order = self.get_order(
            context=context,
            order_id=order_id,
        )

        if order.status == ClinicalOrderStatus.RECEIVED:
            raise ClinicalOrderAlreadyReceivedError(
                "Clinical Order has already been received.",
            )

        if order.status in (
            ClinicalOrderStatus.IN_PROGRESS,
            ClinicalOrderStatus.COMPLETED,
            ClinicalOrderStatus.CANCELLED,
        ):
            raise ClinicalOrderCannotReceiveError(
                "Clinical Order cannot be received from its current status.",
            )

        self._get_authenticated_staff(
            context=context,
        )

        order.status = ClinicalOrderStatus.RECEIVED

        try:
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(order)

        return order


    # ------------------------------------------------------------------
    # Start
    # ------------------------------------------------------------------

    def start_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> ClinicalOrder:
        """
        Move a Clinical Order from REQUESTED to IN_PROGRESS.
        """

        from app.modules.clinical_orders.exceptions import (
            ClinicalOrderAlreadyInProgressError,
            ClinicalOrderAlreadyCompletedError,
            ClinicalOrderCannotStartError,
        )

        order = self.get_order(
            context=context,
            order_id=order_id,
        )

        if order.status == ClinicalOrderStatus.REQUESTED:
            from app.modules.clinical_orders.exceptions import (
                ClinicalOrderCannotStartError,
            )

            raise ClinicalOrderCannotStartError(
                "Clinical Order must be received before it can be started.",
            )

        if order.status == ClinicalOrderStatus.IN_PROGRESS:
            raise ClinicalOrderAlreadyInProgressError(
                "Clinical Order is already in progress.",
            )

        if order.status == ClinicalOrderStatus.COMPLETED:
            raise ClinicalOrderAlreadyCompletedError(
                "Completed Clinical Orders cannot be started.",
            )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise ClinicalOrderCannotStartError(
                "Cancelled Clinical Orders cannot be started.",
            )

        self._get_authenticated_staff(
            context=context,
        )

        order.status = ClinicalOrderStatus.IN_PROGRESS
        order.started_at = datetime.now(UTC)

        try:
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(order)

        return order

    # ------------------------------------------------------------------
    # Receive Clinical Order Item
    # ------------------------------------------------------------------

    def receive_order_item(
        self,
        *,
        context: RequestContext,
        order_item_id: UUID,
    ) -> ClinicalOrder:
        """
        Move a Clinical Order Item from REQUESTED to RECEIVED.

        The parent Clinical Order is returned so callers receive the
        complete aggregate with all item statuses.
        """

        from app.modules.clinical_orders.exceptions import (
            ClinicalOrderItemAlreadyReceivedError,
            ClinicalOrderItemCannotReceiveError,
            ClinicalOrderItemNotFoundError,
        )

        order = self._get_order_for_item(
            context=context,
            order_item_id=order_item_id,
        )

        order_item = next(
            (
                item
                for item in order.items
                if item.id == order_item_id
            ),
            None,
        )

        if order_item is None:
            raise ClinicalOrderItemNotFoundError(
                "Clinical Order Item not found.",
            )

        if order_item.status == ClinicalOrderStatus.RECEIVED:
            raise ClinicalOrderItemAlreadyReceivedError(
                "Clinical Order Item has already been received.",
            )

        if order_item.status in (
            ClinicalOrderStatus.IN_PROGRESS,
            ClinicalOrderStatus.COMPLETED,
            ClinicalOrderStatus.CANCELLED,
        ):
            raise ClinicalOrderItemCannotReceiveError(
                "Clinical Order Item cannot be received from its current status.",
            )

        self._get_authenticated_staff(
            context=context,
        )

        order_item.status = ClinicalOrderStatus.RECEIVED


        try:
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(order)

        return order


    # ------------------------------------------------------------------
    # Start Clinical Order Item
    # ------------------------------------------------------------------

    def start_order_item(
        self,
        *,
        context: RequestContext,
        order_item_id: UUID,
    ) -> ClinicalOrder:
        """
        Move a Clinical Order Item from RECEIVED to IN_PROGRESS.
        """

        from app.modules.clinical_orders.exceptions import (
            ClinicalOrderItemAlreadyCompletedError,
            ClinicalOrderItemAlreadyInProgressError,
            ClinicalOrderItemCannotStartError,
            ClinicalOrderItemNotFoundError,
        )

        order = self._get_order_for_item(
            context=context,
            order_item_id=order_item_id,
        )

        order_item = next(
            (
                item
                for item in order.items
                if item.id == order_item_id
            ),
            None,
        )

        if order_item is None:
            raise ClinicalOrderItemNotFoundError(
                "Clinical Order Item not found.",
            )

        if order_item.status == ClinicalOrderStatus.REQUESTED:
            raise ClinicalOrderItemCannotStartError(
                "Clinical Order Item must be received before it can be started.",
            )

        if order_item.status == ClinicalOrderStatus.IN_PROGRESS:
            raise ClinicalOrderItemAlreadyInProgressError(
                "Clinical Order Item is already in progress.",
            )

        if order_item.status == ClinicalOrderStatus.COMPLETED:
            raise ClinicalOrderItemAlreadyCompletedError(
                "Completed Clinical Order Items cannot be started.",
            )

        if order_item.status == ClinicalOrderStatus.CANCELLED:
            raise ClinicalOrderItemCannotStartError(
                "Cancelled Clinical Order Items cannot be started.",
            )

        self._get_authenticated_staff(
            context=context,
        )

        order_item.status = ClinicalOrderStatus.IN_PROGRESS


        try:
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(order)

        return order


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
