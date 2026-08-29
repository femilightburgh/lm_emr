"""
==============================================================================
LIGHTBURGH EMR

Clinical Order API Router
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
    ClinicalOrderStatus,
)
from app.modules.clinical_orders.exceptions import (
    ClinicalOrderAlreadyCancelledError,
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
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    PrescriptionRepository,
)
from app.modules.clinical_orders.schemas import (
    CreateClinicalOrderRequest,
    ClinicalOrderResponse,
    LaboratoryQueueItemResponse,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
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
            ordered_at=order.ordered_at,
            started_at=order.started_at,
        )
        for order in service.list_laboratory_queue(
            context=context,
        )
    ]


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
