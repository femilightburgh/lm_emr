"""
==============================================================================
LIGHTBURGH EMR

Clinical Order API Router
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.core.security.authorization import require_permission
from app.db.session import get_db

from app.modules.clinical_orders.enums import (
    ClinicalOrderStatus,
)
from app.modules.clinical_orders.exceptions import (
    ClinicalOrderAlreadyCancelledError,
    MedicationAdministrationEpisodeError,
    MedicationAdministrationStaffHospitalMismatchError,
    MedicationAdministrationStaffNotFoundError,
    MedicationDoseAlreadyAdministeredError,
    MedicationDoseCannotBeAdministeredError,
    MedicationDoseNotFoundError,
    ClinicalOrderAlreadyCompletedError,
    ClinicalOrderAlreadyInProgressError,
    ClinicalOrderCannotStartError,
    ClinicalOrderEncounterClosedError,
    ClinicalOrderEpisodeCancelledError,
    ClinicalOrderEpisodeClosedError,
    ClinicalOrderNotFoundError,
    ClinicalOrderStaffHospitalMismatchError,
    ClinicalOrderStaffNotFoundError,
    ClinicalOrderAlreadyReceivedError,
    ClinicalOrderCannotReceiveError,
    ClinicalOrderItemAlreadyReceivedError,
    ClinicalOrderItemCannotReceiveError,
    ClinicalOrderItemNotFoundError,
    ClinicalOrderItemAlreadyInProgressError,
    ClinicalOrderItemAlreadyCompletedError,
    ClinicalOrderItemCannotStartError,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    MedicationAdministrationRepository,
    MedicationTreatmentRepository,
    PrescriptionRepository,
)
from app.modules.diagnostics.repositories.diagnostic_repository import (
    DiagnosticRepository,
)
from app.modules.laboratory.repositories.laboratory_test_repository import (
    LaboratoryTestRepository,
)
from app.modules.clinical_orders.schemas import (
    CreateClinicalOrderRequest,
    CreateMedicationAdministrationRequest,
    CreateMedicationTreatmentRequest,
    ClinicalOrderResponse,
    ClinicalOrderItemResponse,
    LaboratoryQueueItemResponse,
    DiagnosticQueueItemResponse,
    MedicationAdministrationResponse,
    MedicationDoseQueueResponse,
    MedicationTreatmentResponse,
    MedicationNursingSummaryResponse,
    MedicationTreatmentHistoryResponse,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
    InpatientMedicationService,
    MedicationAdministrationService,
    MedicationNursingSummaryService,
    MedicationTreatmentHistoryService,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.identity.permissions import Permissions
from app.modules.staff.repository import StaffRepository


router = APIRouter(
    prefix="/clinical-orders",
    tags=["Clinical Orders"],
)


# ============================================================================
# Dependencies
# ============================================================================


def get_inpatient_medication_service(
    db: Session = Depends(get_db),
) -> InpatientMedicationService:
    """
    Build the inpatient medication service dependency graph.
    """

    return InpatientMedicationService(
        db=db,
        episode_repository=EpisodeRepository(db),
        treatment_repository=MedicationTreatmentRepository(db),
    )


def get_medication_nursing_summary_service(
    db: Session = Depends(get_db),
) -> MedicationNursingSummaryService:
    """
    Build the Nursing medication summary service dependency graph.
    """

    return MedicationNursingSummaryService(
        treatment_repository=MedicationTreatmentRepository(db),
        episode_repository=EpisodeRepository(db),
    )


def get_medication_treatment_history_service(
    db: Session = Depends(get_db),
) -> MedicationTreatmentHistoryService:
    """
    Build the medication treatment history service dependency graph.
    """

    return MedicationTreatmentHistoryService(
        treatment_repository=MedicationTreatmentRepository(db),
    )


def get_medication_administration_service(
    db: Session = Depends(get_db),
) -> MedicationAdministrationService:
    """
    Build the medication administration service dependency graph.
    """

    return MedicationAdministrationService(
        repository=MedicationAdministrationRepository(db),
        treatment_repository=MedicationTreatmentRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )


def get_clinical_order_service(
    db: Session = Depends(get_db),
) -> ClinicalOrderService:
    """
    Build the ClinicalOrderService dependency graph.
    """

    return ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        laboratory_test_repository=LaboratoryTestRepository(db),
        diagnostic_repository=DiagnosticRepository(db),
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )


# ============================================================================
# Create
# ============================================================================


@router.post(
    "",
    response_model=ClinicalOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Clinical Order",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_CREATE,
            ),
        ),
    ],
)
def create_clinical_order(
    request: CreateClinicalOrderRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Create a Clinical Order within an Encounter.
    """

    try:
        order = service.create_order(
            context=context,
            encounter_id=request.encounter_id,
            order_type=request.order_type,
            priority=request.priority,
            details=request.details,
            items=[
                item.model_dump()
                for item in request.items
            ],
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderEncounterClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clinical Orders cannot be created on a closed Encounter.",
        ) from exc

    except ClinicalOrderEpisodeClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clinical Orders cannot be created on a closed Episode.",
        ) from exc

    except ClinicalOrderEpisodeCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clinical Orders cannot be created on a cancelled Episode.",
        ) from exc

    except ClinicalOrderStaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user does not have a Staff profile.",
        ) from exc

    except ClinicalOrderStaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff member does not belong to the authenticated Hospital.",
        ) from exc


# ============================================================================
# Activate Inpatient Medication Treatment
# ============================================================================


@router.post(
    "/medication-treatments",
    response_model=MedicationTreatmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Inpatient Medication Treatment",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_CREATE,
            ),
        ),
    ],
)
def create_inpatient_medication_treatment(
    request: CreateMedicationTreatmentRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: InpatientMedicationService = Depends(
        get_inpatient_medication_service,
    ),
):
    """
    Activate an inpatient medication treatment from a prescription.
    """

    from app.modules.clinical_orders.repositories import (
        PrescriptionRepository,
    )

    prescription = PrescriptionRepository(
        service.db,
    ).get_by_id(
        prescription_id=request.prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    try:
        treatment = service.create_treatment(
            context=context,
            prescription=prescription,
            start_at=request.start_at,
            first_dose_at=request.first_dose_at,
        )

        return MedicationTreatmentResponse.model_validate(
            treatment,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Medication Nursing Summary
# ============================================================================


@router.get(
    "/medication-nursing-summary/episode/{episode_id}",
    response_model=MedicationNursingSummaryResponse,
    summary="Get Nursing Medication Summary",
    dependencies=[
        Depends(
            require_permission(
                Permissions.MEDICATION_ADMINISTRATION_READ,
            ),
        ),
    ],
)
def get_medication_nursing_summary(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: MedicationNursingSummaryService = Depends(
        get_medication_nursing_summary_service,
    ),
):
    """
    Return the inpatient Nursing medication round and summaries.
    """

    try:
        prescriptions, round_groups = (
            service.build_episode_summary(
                context=context,
                episode_id=episode_id,
            )
        )

        return MedicationNursingSummaryResponse.model_validate(
            {
                "prescriptions": prescriptions,
                "round": round_groups,
            }
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Medication Treatment History
# ============================================================================


@router.get(
    "/medication-treatments/{treatment_id}/history",
    response_model=MedicationTreatmentHistoryResponse,
    summary="Get Medication Treatment History",
    dependencies=[
        Depends(
            require_permission(
                Permissions.MEDICATION_ADMINISTRATION_READ,
            ),
        ),
    ],
)
def get_medication_treatment_history(
    treatment_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: MedicationTreatmentHistoryService = Depends(
        get_medication_treatment_history_service,
    ),
):
    """
    Return the complete medication history for one inpatient treatment.
    """

    try:
        history = service.build_history(
            context=context,
            treatment_id=treatment_id,
        )

        return MedicationTreatmentHistoryResponse.model_validate(
            history,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Medication Administration
# ============================================================================


@router.get(
    "/medication-doses/episode/{episode_id}",
    response_model=list[MedicationDoseQueueResponse],
    summary="List Episode Medication Doses",
    dependencies=[
        Depends(
            require_permission(
                Permissions.MEDICATION_ADMINISTRATION_READ,
            ),
        ),
    ],
)
def list_episode_medication_doses(
    episode_id: UUID,
    from_time: datetime | None = Query(
        default=None,
        description="Start of the medication-dose window.",
    ),
    to_time: datetime | None = Query(
        default=None,
        description="End of the medication-dose window.",
    ),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: MedicationAdministrationService = Depends(
        get_medication_administration_service,
    ),
):
    """
    Return scheduled medication doses for an admitted Episode.
    """

    now = datetime.now(UTC)

    effective_from = (
        from_time
        if from_time is not None
        else now - timedelta(days=1)
    )

    effective_to = (
        to_time
        if to_time is not None
        else now + timedelta(days=1)
    )

    if effective_from > effective_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_time cannot be later than to_time.",
        )

    try:
        doses = service.list_episode_doses(
            context=context,
            episode_id=episode_id,
            from_time=effective_from,
            to_time=effective_to,
        )

        results = []

        for dose in doses:
            treatment = dose.treatment
            prescription = (
                treatment.prescription
                if treatment is not None
                else None
            )

            if treatment is None or prescription is None:
                continue

            administration = dose.administration

            results.append(
                {
                    "id": dose.id,
                    "treatment_id": treatment.id,
                    "scheduled_at": dose.scheduled_at,
                    "status": dose.status,
                    "treatment_status": treatment.status,
                    "medicine_name": prescription.medicine_name,
                    "strength": prescription.strength,
                    "dose": prescription.dose,
                    "dose_unit": prescription.dose_unit,
                    "route": prescription.route,
                    "frequency": prescription.frequency,
                    "duration": prescription.duration,
                    "duration_unit": prescription.duration_unit,
                    "directions": prescription.directions,
                    "administration": (
                        MedicationAdministrationResponse.model_validate(
                            administration,
                        )
                        if administration is not None
                        else None
                    ),
                }
            )

        return [
            MedicationDoseQueueResponse.model_validate(
                result,
            )
            for result in results
        ]

    except MedicationDoseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except MedicationAdministrationEpisodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/medication-doses/{dose_id}/administration",
    response_model=MedicationAdministrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Medication Administration",
    dependencies=[
        Depends(
            require_permission(
                Permissions.MEDICATION_ADMINISTRATION_CREATE,
            ),
        ),
    ],
)
def create_medication_administration(
    dose_id: UUID,
    request: CreateMedicationAdministrationRequest,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: MedicationAdministrationService = Depends(
        get_medication_administration_service,
    ),
):
    """
    Record the nursing outcome of a scheduled medication dose.
    """

    try:
        administration = service.record_administration(
            context=context,
            dose_id=dose_id,
            status=request.status,
            administered_at=request.administered_at,
            dose_given=request.dose_given,
            reason=request.reason,
            notes=request.notes,
        )

        db.commit()
        db.refresh(administration)

        return MedicationAdministrationResponse.model_validate(
            administration,
        )

    except (
        MedicationAdministrationStaffNotFoundError,
        MedicationDoseNotFoundError,
    ) as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        MedicationAdministrationStaffHospitalMismatchError,
    ) as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except (
        MedicationDoseAlreadyAdministeredError,
        MedicationDoseCannotBeAdministeredError,
        MedicationAdministrationEpisodeError,
    ) as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Retrieve
# ============================================================================


@router.get(
    "/{order_id}",
    response_model=ClinicalOrderResponse,
    summary="Retrieve Clinical Order",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def get_clinical_order(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Retrieve a Clinical Order.
    """

    try:
        order = service.get_order(
            context=context,
            order_id=order_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc


# ============================================================================
# List Encounter Orders
# ============================================================================


@router.get(
    "/episodes/{episode_id}",
    response_model=list[ClinicalOrderResponse],
    summary="List Episode Clinical Orders",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_episode_clinical_orders(
    episode_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Return all Clinical Orders belonging to an Episode.

    Orders remain attached to their original Encounters. This endpoint
    exposes the complete Episode investigation history for clinical
    workflows such as Doctor Review.
    """

    return [
        ClinicalOrderResponse.model_validate(order)
        for order in service.list_episode_orders(
            context=context,
            episode_id=episode_id,
        )
    ]


@router.get(
    "/encounters/{encounter_id}",
    response_model=list[ClinicalOrderResponse],
    summary="List Encounter Clinical Orders",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_encounter_clinical_orders(
    encounter_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Return all Clinical Orders belonging to an Encounter.
    """

    return [
        ClinicalOrderResponse.model_validate(order)
        for order in service.list_encounter_orders(
            context=context,
            encounter_id=encounter_id,
        )
    ]


# ============================================================================
# Laboratory Queue
# ============================================================================


@router.get(
    "/queue/laboratory",
    response_model=list[LaboratoryQueueItemResponse],
    summary="List Laboratory Queue",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_laboratory_queue(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Return laboratory orders currently requiring laboratory attention.
    """

    return [
        LaboratoryQueueItemResponse(
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
            items=[
                ClinicalOrderItemResponse.model_validate(item)
                for item in order.items
            ],
            ordered_at=order.ordered_at,
            started_at=order.started_at,
        )
        for order in service.list_laboratory_queue(
            context=context,
        )
    ]


# ============================================================================
# Diagnostics Queue
# ============================================================================


@router.get(
    "/queue/diagnostics",
    response_model=list[DiagnosticQueueItemResponse],
    summary="List Diagnostics Queue",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_diagnostic_queue(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Return diagnostic orders currently requiring diagnostic attention.
    """

    return [
        DiagnosticQueueItemResponse(
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
            items=[
                ClinicalOrderItemResponse.model_validate(item)
                for item in order.items
            ],
            ordered_at=order.ordered_at,
            started_at=order.started_at,
        )
        for order in service.list_diagnostic_queue(
            context=context,
        )
    ]



# ============================================================================
# Receive Clinical Order Item
# ============================================================================


@router.post(
    "/items/{item_id}/receive",
    response_model=ClinicalOrderResponse,
    summary="Receive Clinical Order Item",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def receive_clinical_order_item(
    item_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    try:
        order = service.receive_order_item(
            context=context,
            order_item_id=item_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order Item not found.",
        ) from exc

    except ClinicalOrderItemAlreadyReceivedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderItemCannotReceiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Start Clinical Order Item
# ============================================================================


@router.post(
    "/items/{item_id}/start",
    response_model=ClinicalOrderResponse,
    summary="Start Clinical Order Item",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def start_clinical_order_item(
    item_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    try:
        order = service.start_order_item(
            context=context,
            order_item_id=item_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order Item not found.",
        ) from exc

    except ClinicalOrderItemAlreadyInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderItemAlreadyCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderItemCannotStartError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Receive
# ============================================================================


@router.post(
    "/{order_id}/receive",
    response_model=ClinicalOrderResponse,
    summary="Receive Clinical Order",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def receive_clinical_order(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    try:
        order = service.receive_order(
            context=context,
            order_id=order_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc

    except ClinicalOrderAlreadyReceivedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderCannotReceiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Start
# ============================================================================


@router.post(
    "/{order_id}/start",
    response_model=ClinicalOrderResponse,
    summary="Start Clinical Order",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def start_clinical_order(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Move a Clinical Order from REQUESTED to IN_PROGRESS.
    """

    try:
        order = service.start_order(
            context=context,
            order_id=order_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc

    except ClinicalOrderAlreadyInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderAlreadyCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalOrderCannotStartError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Cancel
# ============================================================================


@router.post(
    "/{order_id}/cancel",
    response_model=ClinicalOrderResponse,
    summary="Cancel Clinical Order",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_CANCEL,
            ),
        ),
    ],
)
def cancel_clinical_order(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalOrderService = Depends(
        get_clinical_order_service,
    ),
):
    """
    Cancel a Clinical Order.
    """

    try:
        order = service.cancel_order(
            context=context,
            order_id=order_id,
        )

        return ClinicalOrderResponse.model_validate(
            order,
        )

    except ClinicalOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc

    except ClinicalOrderAlreadyCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Completed Clinical Orders cannot be cancelled.",
        ) from exc

    except ClinicalOrderAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clinical Order is already cancelled.",
        ) from exc

    except ClinicalOrderStaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user does not have a Staff profile.",
        ) from exc

    except ClinicalOrderStaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff member does not belong to the authenticated Hospital.",
        ) from exc
