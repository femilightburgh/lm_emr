"""
==============================================================================
LIGHTBURGH EMR

Diagnostics API Router
==============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.core.security.authorization import require_permission
from app.db.session import get_db
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.clinical_results.enums import ClinicalResultStatus
from app.modules.diagnostics.enums import DiagnosticCategory
from app.modules.diagnostics.exceptions import (
    DiagnosticCategoryMismatchError,
    DiagnosticInvestigationNotFoundError,
    DiagnosticReportAlreadyExistsError,
    DiagnosticReportFinalizedError,
    DiagnosticReportNotFoundError,
    DiagnosticReportOrderCancelledError,
    DiagnosticReportOrderNotFoundError,
    DiagnosticReportOrderNotInProgressError,
    DiagnosticReportStaffHospitalMismatchError,
    DiagnosticReportStaffNotFoundError,
)
from app.modules.diagnostics.repositories import (
    DiagnosticRepository,
)
from app.modules.diagnostics.schemas import (
    DiagnosticInvestigationResponse,
    DiagnosticReportCreateRequest,
    DiagnosticReportResponse,
    DiagnosticReportUpdateRequest,
    DiagnosticReportAttachmentResponse,
)
from app.modules.diagnostics.services import (
    DiagnosticService,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_clinical_workflow_service import (
    EpisodeClinicalWorkflowService,
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
from app.storage import LocalStorage


router = APIRouter(
    prefix="/diagnostics",
    tags=["Diagnostics"],
)


# ============================================================================
# Dependencies
# ============================================================================


def get_diagnostic_service(
    db: Session = Depends(get_db),
) -> DiagnosticService:
    return DiagnosticService(
        repository=DiagnosticRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        storage=LocalStorage(
            settings.storage_path,
        ),
        episode_clinical_workflow_service=(
            EpisodeClinicalWorkflowService(
                clinical_order_repository=ClinicalOrderRepository(db),
                encounter_service=EncounterService(
                    repository=EncounterRepository(db),
                    episode_repository=EpisodeRepository(db),
                    staff_repository=StaffRepository(db),
                ),
            )
        ),
    )


# ============================================================================
# Investigations
# ============================================================================


@router.get(
    "/investigations",
    response_model=list[DiagnosticInvestigationResponse],
    summary="List Diagnostic Investigations",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def list_diagnostic_investigations(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    return service.list_investigations(
        hospital_id=context.hospital_id,
    )


@router.get(
    "/investigations/{investigation_id}",
    response_model=DiagnosticInvestigationResponse,
    summary="Get Diagnostic Investigation",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_ORDER_READ,
            ),
        ),
    ],
)
def get_diagnostic_investigation(
    investigation_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.get_investigation(
            hospital_id=context.hospital_id,
            investigation_id=investigation_id,
        )

    except DiagnosticInvestigationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================================
# Reports
# ============================================================================


@router.post(
    "/reports",
    response_model=DiagnosticReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Diagnostic Report",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def create_diagnostic_report(
    request: DiagnosticReportCreateRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.create_report(
            context=context,
            order_id=request.order_id,
            investigation_id=request.investigation_id,
            category=request.category,
            findings=request.findings,
            impression=request.impression,
            interpretation=request.interpretation,
            recommendations=request.recommendations,
            measurements=request.measurements,
        )

    except DiagnosticReportOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticReportOrderCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DiagnosticReportOrderNotInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DiagnosticInvestigationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticCategoryMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except DiagnosticReportAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/reports/by-order/{order_id}",
    response_model=DiagnosticReportResponse,
    summary="Get Diagnostic Report By Clinical Order",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_READ,
            ),
        ),
    ],
)
def get_diagnostic_report_by_order(
    order_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.get_report_by_order(
            context=context,
            order_id=order_id,
        )

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/reports/{report_id}",
    response_model=DiagnosticReportResponse,
    summary="Get Diagnostic Report",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_READ,
            ),
        ),
    ],
)
def get_diagnostic_report(
    report_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.get_report(
            context=context,
            report_id=report_id,
        )

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/reports/{report_id}",
    response_model=DiagnosticReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Draft Diagnostic Report",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def update_diagnostic_report(
    report_id: UUID,
    request: DiagnosticReportUpdateRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.update_report(
            context=context,
            report_id=report_id,
            findings=request.findings,
            impression=request.impression,
            interpretation=request.interpretation,
            recommendations=request.recommendations,
            measurements=request.measurements,
        )

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticReportFinalizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/reports/{report_id}/finalize",
    response_model=DiagnosticReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize Diagnostic Report",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def finalize_diagnostic_report(
    report_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.finalize_report(
            context=context,
            report_id=report_id,
        )

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticReportFinalizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DiagnosticReportOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticReportOrderCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DiagnosticReportOrderNotInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DiagnosticReportStaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticReportStaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

# ============================================================================
# Attachments
# ============================================================================


@router.post(
    "/reports/{report_id}/attachments",
    response_model=DiagnosticReportAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Diagnostic Report Attachment",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_CREATE,
            ),
        ),
    ],
)
def upload_diagnostic_report_attachment(
    report_id: UUID,
    file: UploadFile = File(...),
    description: str | None = Form(default=None),
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        allowed_types = {
            item.strip()
            for item in settings.storage_allowed_content_types.split(",")
            if item.strip()
        }

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    "Unsupported file type. Allowed types: "
                    + ", ".join(sorted(allowed_types))
                ),
            )

        content = file.file.read()

        max_bytes = (
            settings.storage_max_file_size_mb
            * 1024
            * 1024
        )

        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=(
                    f"File exceeds the maximum allowed size "
                    f"of {settings.storage_max_file_size_mb} MB."
                ),
            )

        attachment = service.create_attachment(
            context=context,
            report_id=report_id,
            file_name=file.filename or "attachment",
            content_type=file.content_type,
            content=content,
            description=description,
        )

        return attachment

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DiagnosticReportFinalizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================================
# Attachment Retrieval
# ============================================================================


@router.get(
    "/reports/{report_id}/attachments",
    response_model=list[DiagnosticReportAttachmentResponse],
    summary="List Diagnostic Report Attachments",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_READ,
            ),
        ),
    ],
)
def list_diagnostic_report_attachments(
    report_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        return service.list_attachments(
            context=context,
            report_id=report_id,
        )

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/attachments/{attachment_id}",
    summary="Download Diagnostic Report Attachment",
    dependencies=[
        Depends(
            require_permission(
                Permissions.CLINICAL_RESULT_READ,
            ),
        ),
    ],
)
def download_diagnostic_report_attachment(
    attachment_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: DiagnosticService = Depends(
        get_diagnostic_service,
    ),
):
    try:
        attachment, content = service.get_attachment_content(
            context=context,
            attachment_id=attachment_id,
        )

        return Response(
            content=content,
            media_type=attachment.content_type,
            headers={
                "Content-Disposition": (
                    f'inline; filename="{attachment.file_name}"'
                ),
            },
        )

    except DiagnosticReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
