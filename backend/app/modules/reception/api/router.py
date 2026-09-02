"""
==============================================================================
LIGHTBURGH EMR

Reception API Router
==============================================================================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.core.security.authorization import (
    require_permission,
)
from app.db.session import get_db
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.organization.repository import (
    HospitalRepository,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.reception.schemas import (
    ReceptionOverviewResponse,
    ReceptionPatientFlowResponse,
)
from app.modules.reception.services import (
    ReceptionService,
)


router = APIRouter(
    prefix="/reception",
    tags=["Reception"],
)


def get_reception_service(
    db: Session = Depends(get_db),
) -> ReceptionService:
    """
    Build the ReceptionService dependency graph.
    """
    return ReceptionService(
        patient_repository=PatientRepository(db),
        episode_repository=EpisodeRepository(db),
        hospital_repository=HospitalRepository(db),
    )


@router.get(
    "/patient-flow",
    response_model=ReceptionPatientFlowResponse,
    summary="Get Reception Patient Flow",
    dependencies=[
        Depends(
            require_permission("patient.read"),
        ),
    ],
)
def get_reception_patient_flow(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ReceptionService = Depends(
        get_reception_service,
    ),
) -> ReceptionPatientFlowResponse:
    """
    Return active hospital-scoped patient-flow records.
    """
    return service.list_patient_flow(
        hospital_id=context.hospital_id,
    )


@router.get(
    "/overview",
    response_model=ReceptionOverviewResponse,
    summary="Get Reception Overview",
    dependencies=[
        Depends(
            require_permission("patient.read"),
        ),
    ],
)
def get_reception_overview(
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ReceptionService = Depends(
        get_reception_service,
    ),
) -> ReceptionOverviewResponse:
    """
    Return hospital-scoped Reception overview statistics.
    """
    return service.get_overview(
        hospital_id=context.hospital_id,
    )
