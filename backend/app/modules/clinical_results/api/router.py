"""
==============================================================================
LIGHTBURGH EMR

Clinical Result API Router
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

from app.modules.clinical_results.enums import (
    ClinicalResultStatus,
)
from app.modules.clinical_results.exceptions import (
    ClinicalResultAlreadyFinalError,
    ClinicalResultDuplicateAnalyteError,
    ClinicalResultInvalidValueError,
    ClinicalResultLaboratoryTestNotFoundError,
    ClinicalResultMissingRequiredAnalyteError,
    ClinicalResultNotFoundError,
    ClinicalResultOrderAlreadyCompletedError,
    ClinicalResultOrderNotInProgressError,
    ClinicalResultOrderCancelledError,
    ClinicalResultOrderNotFoundError,
    ClinicalResultStaffHospitalMismatchError,
    ClinicalResultStaffNotFoundError,
    ClinicalResultUnknownAnalyteError,
    ClinicalResultUnsupportedOrderTypeError,
)
from app.modules.clinical_results.repositories import (
    ClinicalResultRepository,
)
from app.modules.clinical_results.schemas import (
    ClinicalResultResponse,
    CreateClinicalResultRequest,
)
from app.modules.clinical_results.services import (
    ClinicalResultService,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.identity.permissions import Permissions
from app.modules.staff.repository import StaffRepository


router = APIRouter(
    prefix="/clinical-results",
    tags=["Clinical Results"],
)


def get_clinical_result_service(
    db: Session = Depends(get_db),
) -> ClinicalResultService:
    episode_repository = EpisodeRepository(db)
    staff_repository = StaffRepository(db)

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=episode_repository,
        staff_repository=staff_repository,
    )

    return ClinicalResultService(
        repository=ClinicalResultRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        episode_repository=episode_repository,
        encounter_service=encounter_service,
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=staff_repository,
    )


# ============================================================================
# Create
# ============================================================================


@router.post(
    "",
    response_model=ClinicalResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Clinical Result",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def record_clinical_result(
    request: CreateClinicalResultRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalResultService = Depends(
        get_clinical_result_service,
    ),
):
    try:
        result = service.record_result(
            context=context,
            order_id=request.order_id,
            order_item_id=request.order_item_id,
            result_type=request.result_type,
            status=request.status,
            result_data=request.result_data,
            values=request.values,
            specimen=request.specimen,
            collected_at=request.collected_at,
            reported_at=request.reported_at,
            interpretation=request.interpretation,
        )

        return ClinicalResultResponse.model_validate(
            result,
        )

    except ClinicalResultOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc

    except ClinicalResultOrderCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultOrderAlreadyCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultLaboratoryTestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ClinicalResultUnknownAnalyteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except ClinicalResultDuplicateAnalyteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except ClinicalResultInvalidValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except ClinicalResultMissingRequiredAnalyteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except ClinicalResultUnsupportedOrderTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultStaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ClinicalResultStaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


# ============================================================================
# Update Draft
# ============================================================================


@router.put(
    "/{result_id}",
    response_model=ClinicalResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Draft Clinical Result",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def update_clinical_result(
    result_id: UUID,
    request: CreateClinicalResultRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalResultService = Depends(
        get_clinical_result_service,
    ),
):
    try:
        if request.status != ClinicalResultStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Only DRAFT Clinical Results can be updated.",
            )

        result = service.update_draft_result(
            context=context,
            result_id=result_id,
            result_data=request.result_data,
            values=request.values,
            specimen=request.specimen,
            collected_at=request.collected_at,
            reported_at=request.reported_at,
            interpretation=request.interpretation,
        )

        return ClinicalResultResponse.model_validate(
            result,
        )

    except ClinicalResultNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ClinicalResultAlreadyFinalError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultOrderNotInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultOrderCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultLaboratoryTestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ClinicalResultUnknownAnalyteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except ClinicalResultDuplicateAnalyteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except ClinicalResultInvalidValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except ClinicalResultMissingRequiredAnalyteError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Finalize
# ============================================================================


@router.post(
    "/{result_id}/finalize",
    response_model=ClinicalResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize Clinical Result",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def finalize_clinical_result(
    result_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalResultService = Depends(
        get_clinical_result_service,
    ),
):
    try:
        result = service.finalize_result(
            context=context,
            result_id=result_id,
        )

        return ClinicalResultResponse.model_validate(
            result,
        )

    except ClinicalResultNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ClinicalResultAlreadyFinalError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultOrderNotInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ClinicalResultOrderCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Retrieve
# ============================================================================


@router.get(
    "/{result_id}",
    response_model=ClinicalResultResponse,
    summary="Retrieve Clinical Result",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_READ,
            ),
        ),
    ],
)
def get_clinical_result(
    result_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalResultService = Depends(
        get_clinical_result_service,
    ),
):
    try:
        result = service.get_result(
            context=context,
            result_id=result_id,
        )

        return ClinicalResultResponse.model_validate(
            result,
        )

    except ClinicalResultOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Result not found.",
        ) from exc


# ============================================================================
# List Order Results
# ============================================================================


@router.get(
    "/orders/{order_id}",
    response_model=list[ClinicalResultResponse],
    summary="List Clinical Order Results",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_READ,
            ),
        ),
    ],
)
def list_order_results(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalResultService = Depends(
        get_clinical_result_service,
    ),
):
    try:
        results = service.list_order_results(
            context=context,
            order_id=order_id,
        )

        return [
            ClinicalResultResponse.model_validate(
                result,
            )
            for result in results
        ]

    except ClinicalResultOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Order not found.",
        ) from exc
