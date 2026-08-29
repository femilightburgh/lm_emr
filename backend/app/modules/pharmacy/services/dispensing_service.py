"""
==============================================================================
LIGHTBURGH EMR

Dispensing Service
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
    ClinicalOrderNotFoundError,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    PrescriptionRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.pharmacy.models import Dispensing
from app.modules.pharmacy.repositories import (
    DispensingRepository,
)
from app.modules.staff.repository import StaffRepository


class DispensingService:
    """
    Business logic for medication dispensing.
    """

    def __init__(
        self,
        *,
        dispensing_repository: DispensingRepository,
        clinical_order_repository: ClinicalOrderRepository,
        prescription_repository: PrescriptionRepository,
        event_service: ClinicalEventService,
        staff_repository: StaffRepository,
    ) -> None:
        self.dispensing_repository = dispensing_repository
        self.clinical_order_repository = clinical_order_repository
        self.prescription_repository = prescription_repository
        self.event_service = event_service
        self.staff_repository = staff_repository

    def dispense(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
        quantity_dispensed: str,
        notes: str | None = None,
    ) -> Dispensing:
        order = self.clinical_order_repository.get_by_id(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

        if order is None:
            raise ClinicalOrderNotFoundError(
                "Clinical Order not found.",
            )

        if order.order_type != ClinicalOrderType.MEDICATION:
            raise ValueError(
                "Only medication orders can be dispensed through Pharmacy.",
            )

        if order.status != ClinicalOrderStatus.IN_PROGRESS:
            raise ValueError(
                "Only medication orders in progress can be dispensed.",
            )

        staff = self.staff_repository.get_by_user_account_id(
            hospital_id=context.hospital_id,
            user_account_id=context.user_id,
        )

        if staff is None:
            raise ValueError(
                "Authenticated user does not have a Staff profile.",
            )

        prescription = self.prescription_repository.get_by_order_id(
            order_id=order.id,
        )

        if prescription is None:
            raise ValueError(
                "Prescription not found for this medication order.",
            )

        existing = self.dispensing_repository.get_by_prescription_id(
            prescription_id=prescription.id,
        )

        if existing is not None:
            raise ValueError(
                "Prescription has already been dispensed.",
            )

        quantity = quantity_dispensed.strip()

        if not quantity:
            raise ValueError(
                "Quantity dispensed is required.",
            )

        dispensed_at = datetime.now(UTC)

        dispensing = Dispensing(
            prescription_id=prescription.id,
            dispensed_by=staff.id,
            quantity_dispensed=quantity,
            dispensed_at=dispensed_at,
            notes=notes.strip() if notes else None,
        )

        try:
            self.dispensing_repository.create(
                dispensing=dispensing,
            )

            order.status = ClinicalOrderStatus.COMPLETED
            order.completed_at = dispensed_at

            self.event_service.create_event(
                context=context,
                encounter_id=order.encounter_id,
                event_type=EventType.MEDICATION_DISPENSED,
                performed_by=staff.id,
                occurred_at=dispensed_at,
                payload={
                    "clinical_order_id": str(order.id),
                    "prescription_id": str(prescription.id),
                    "quantity_dispensed": quantity,
                },
                commit=False,
            )

            self.dispensing_repository.db.commit()

        except Exception:
            self.dispensing_repository.db.rollback()
            raise

        self.dispensing_repository.db.refresh(dispensing)
        self.dispensing_repository.db.refresh(order)

        return dispensing
