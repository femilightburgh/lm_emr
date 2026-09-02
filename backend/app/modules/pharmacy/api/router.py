"""
==============================================================================
LIGHTBURGH EMR

Pharmacy API
==============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.core.security.authorization import require_permission
from app.db.session import get_db
from app.modules.clinical_orders.enums import (
    ClinicalOrderType,
)
from app.modules.clinical_orders.exceptions import (
    ClinicalOrderEncounterClosedError,
    ClinicalOrderEpisodeCancelledError,
    ClinicalOrderEpisodeClosedError,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    MedicationTreatmentRepository,
    PrescriptionRepository,
)
from app.modules.clinical_orders.schemas import (
    CreatePrescriptionRequest,
    ClinicalOrderResponse,
    PrescriptionResponse,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
    InpatientMedicationService,
)
from app.modules.pharmacy.repositories import (
    DispensingRepository,
)
from app.modules.pharmacy.services import (
    DispensingService,
)
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.identity.permissions import Permissions
from app.modules.pharmacy.schemas import (
    DispensePrescriptionRequest,
    DispensePrescriptionResponse,
    PharmacyQueueItemResponse,
)
from app.modules.staff.repository import StaffRepository


router = APIRouter(
    prefix="/prescriptions",
    tags=["Prescriptions"],
)


def get_clinical_order_service(
    db: Session = Depends(get_db),
) -> ClinicalOrderService:
    return ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )


@router.get(
    "/queue",
    response_model=list[PharmacyQueueItemResponse],
    summary="List Pharmacy Queue",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_pharmacy_queue(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Return medication orders currently requiring pharmacy attention.
    """

    return [
        PharmacyQueueItemResponse(
            id=order.id,
            encounter_id=order.encounter_id,
            patient_id=order.encounter.episode.patient_id,
            patient_name=(
                f"{order.encounter.episode.patient.first_name} "
                f"{order.encounter.episode.patient.last_name}"
            ),
            hospital_number=(
                order.encounter.episode.patient.hospital_number
            ),
            episode_number=(
                order.encounter.episode.episode_number
            ),
            ordering_clinician_name=(
                f"{order.ordering_staff.first_name} "
                f"{order.ordering_staff.last_name}"
            ),
            order_type=order.order_type,
            status=order.status,
            priority=order.priority,
            details=order.details,
            prescription_id=(
                order.prescription.id
                if order.prescription is not None
                else None
            ),
            medicine_name=(
                order.prescription.medicine_name
                if order.prescription is not None
                else None
            ),
            strength=(
                order.prescription.strength
                if order.prescription is not None
                else None
            ),
            dose=(
                order.prescription.dose
                if order.prescription is not None
                else None
            ),
            dose_unit=(
                order.prescription.dose_unit
                if order.prescription is not None
                else None
            ),
            route=(
                order.prescription.route
                if order.prescription is not None
                else None
            ),
            frequency=(
                order.prescription.frequency
                if order.prescription is not None
                else None
            ),
            duration=(
                order.prescription.duration
                if order.prescription is not None
                else None
            ),
            duration_unit=(
                order.prescription.duration_unit
                if order.prescription is not None
                else None
            ),
            quantity=(
                order.prescription.quantity
                if order.prescription is not None
                else None
            ),
            directions=(
                order.prescription.directions
                if order.prescription is not None
                else None
            ),
            indication=(
                order.prescription.indication
                if order.prescription is not None
                else None
            ),
            ordered_at=order.ordered_at,
            started_at=order.started_at,
        )
        for order in service.list_pharmacy_queue(
            context=context,
        )
    ]


@router.post(
    "/{order_id}/receive",
    response_model=ClinicalOrderResponse,
    summary="Receive Prescription",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def receive_prescription(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    try:
        order = service.get_order(
            context=context,
            order_id=order_id,
        )

        if order.order_type != ClinicalOrderType.MEDICATION:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only medication orders can be received "
                    "through Pharmacy."
                ),
            )

        order = service.receive_order(
            context=context,
            order_id=order_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except HTTPException:
        raise

@router.post(
    "/{order_id}/start",
    response_model=ClinicalOrderResponse,
    summary="Start Prescription Processing",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def start_prescription(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    try:
        order = service.get_order(
            context=context,
            order_id=order_id,
        )

        if order.order_type != ClinicalOrderType.MEDICATION:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only medication orders can be started "
                    "through Pharmacy."
                ),
            )

        order = service.start_order(
            context=context,
            order_id=order_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except HTTPException:
        raise

@router.post(
    "/{order_id}/dispense",
    response_model=DispensePrescriptionResponse,
    summary="Dispense Prescription",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def dispense_prescription(
    order_id: UUID,
    request: DispensePrescriptionRequest,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(
        get_request_context,
    ),
):
    service = DispensingService(
        dispensing_repository=DispensingRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        prescription_repository=PrescriptionRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
    )

    try:
        dispensing = service.dispense(
            context=context,
            order_id=order_id,
            quantity_dispensed=request.quantity_dispensed,
            notes=request.notes,
        )

        return DispensePrescriptionResponse.model_validate(
            dispensing,
        )

    except HTTPException:
        raise

    except ClinicalOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Prescription",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_CREATE,
            ),
        ),
    ],
)
def create_prescription(
    request: CreatePrescriptionRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    try:
        details = {
            "medication_id": request.medicine_name,
            "medicine_name": request.medicine_name,
            "strength": request.strength,
            "dose": request.dose,
            "dose_unit": request.dose_unit,
            "route": request.route,
            "frequency": request.frequency,
            "duration": request.duration,
            "duration_unit": request.duration_unit,
            "quantity": request.quantity,
            "directions": request.directions,
            "indication": request.indication,
        }

        order = service.create_order(
            context=context,
            encounter_id=request.encounter_id,
            order_type=ClinicalOrderType.MEDICATION,
            priority=request.priority,
            details=details,
            start_at=request.start_at,
            first_dose_at=request.first_dose_at,
        )

        prescription = order.prescription

        if prescription is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prescription was not created.",
            )

        return PrescriptionResponse.model_validate(
            prescription,
        )

    except ClinicalOrderEncounterClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderEpisodeClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderEpisodeCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
