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
    Prescription,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    PrescriptionRepository,
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
        inpatient_medication_service: InpatientMedicationService | None = None,
    ) -> None:
        self.repository = repository
        self.event_service = event_service
        self.encounter_repository = encounter_repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository
        self.prescription_repository = prescription_repository
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
            if order_type == ClinicalOrderType.DIAGNOSTIC:
                from app.modules.diagnostics.repositories import (
                    DiagnosticRepository,
                )

                investigation_id = details.get(
                    "investigation_id",
                )

                if not investigation_id:
                    raise ValueError(
                        "Diagnostic orders require an investigation_id."
                    )

                diagnostic_repository = DiagnosticRepository(
                    self.repository.db,
                )

                investigation = diagnostic_repository.get_investigation(
                    hospital_id=context.hospital_id,
                    investigation_id=investigation_id,
                )

                if investigation is None:
                    raise ValueError(
                        "Diagnostic investigation not found."
                    )

                details = {
                    **details,
                    "investigation_id": str(
                        investigation.id,
                    ),
                    "investigation_code": investigation.code,
                    "investigation_name": investigation.name,
                    "diagnostic_category": investigation.category.value,
                }

                order.details = details

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
