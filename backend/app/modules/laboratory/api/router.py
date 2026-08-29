"""
==============================================================================
LIGHTBURGH EMR

Laboratory Test API
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
from app.modules.identity.permissions import Permissions
from app.modules.laboratory.exceptions import (
    LaboratoryAnalyteNotFoundError,
    LaboratoryReferenceRangeError,
    LaboratoryTestNotFoundError,
)
from app.modules.laboratory.repositories import (
    LaboratoryTestRepository,
)
from app.modules.laboratory.schemas import (
    CreateLaboratoryAnalyteRequest,
    CreateLaboratoryTestRequest,
    LaboratoryTestAnalyteResponse,
    LaboratoryTestResponse,
    UpdateLaboratoryAnalyteRequest,
)
from app.modules.laboratory.services import (
    LaboratoryTestService,
)


router = APIRouter(
    prefix="/laboratory",
    tags=["Laboratory"],
)


def get_laboratory_test_service(
    db: Session = Depends(get_db),
) -> LaboratoryTestService:
    return LaboratoryTestService(
        repository=LaboratoryTestRepository(db),
    )


@router.post(
    "/tests",
    response_model=LaboratoryTestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Laboratory Test",
    dependencies=[
        Depends(
            require_permission(
                Permissions.LABORATORY_CATALOGUE_UPDATE,
            ),
        ),
    ],
)
def create_laboratory_test(
    request: CreateLaboratoryTestRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: LaboratoryTestService = Depends(
        get_laboratory_test_service,
    ),
):
    try:
        return service.create_test(
            hospital_id=context.hospital_id,
            code=request.code,
            name=request.name,
            specimen=request.specimen,
            description=request.description,
            analytes=[
                analyte.model_dump()
                for analyte in request.analytes
            ],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.post(
    "/tests/{test_code}/analytes",
    response_model=LaboratoryTestAnalyteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Laboratory Analyte",
    dependencies=[
        Depends(
            require_permission(
                Permissions.LABORATORY_CATALOGUE_UPDATE,
            ),
        ),
    ],
)
def create_laboratory_analyte(
    test_code: str,
    request: CreateLaboratoryAnalyteRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: LaboratoryTestService = Depends(
        get_laboratory_test_service,
    ),
):
    try:
        analyte = service.create_analyte(
            hospital_id=context.hospital_id,
            test_code=test_code,
            code=request.code,
            name=request.name,
            data_type=request.data_type,
            unit=request.unit,
            reference_low=request.reference_low,
            reference_high=request.reference_high,
            reference_text=request.reference_text,
            options=request.options,
            required=request.required,
            display_order=request.display_order,
        )

        return LaboratoryTestAnalyteResponse.model_validate(
            analyte,
        )

    except LaboratoryTestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except LaboratoryReferenceRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/tests/{test_code}/analytes/{analyte_id}",
    response_model=LaboratoryTestAnalyteResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Laboratory Analyte",
    dependencies=[
        Depends(
            require_permission(
                Permissions.LABORATORY_CATALOGUE_UPDATE,
            ),
        ),
    ],
)
def update_laboratory_analyte(
    test_code: str,
    analyte_id: UUID,
    request: UpdateLaboratoryAnalyteRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: LaboratoryTestService = Depends(
        get_laboratory_test_service,
    ),
):
    try:
        updates = request.model_dump(
            exclude_unset=True,
        )

        analyte = service.update_analyte(
            hospital_id=context.hospital_id,
            test_code=test_code,
            analyte_id=analyte_id,
            updates=updates,
        )

        return LaboratoryTestAnalyteResponse.model_validate(
            analyte,
        )

    except LaboratoryTestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except LaboratoryAnalyteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except LaboratoryReferenceRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.get(
    "/tests",
    response_model=list[LaboratoryTestResponse],
    summary="List Laboratory Tests",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_laboratory_tests(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: LaboratoryTestService = Depends(
        get_laboratory_test_service,
    ),
):
    return [
        LaboratoryTestResponse.model_validate(test)
        for test in service.list_active_tests(
            hospital_id=context.hospital_id,
        )
    ]
