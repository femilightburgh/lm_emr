from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import RequestContext, get_request_context
from app.core.security.authorization import require_permission
from app.db.session import get_db

from app.modules.diagnoses.exceptions import (
    ClinicalDiagnosisEncounterClosedError,
    ClinicalDiagnosisEncounterNotFoundError,
    ClinicalDiagnosisEpisodeCancelledError,
    ClinicalDiagnosisEpisodeClosedError,
    ClinicalDiagnosisEpisodeNotFoundError,
    ClinicalDiagnosisNotFoundError,
    ClinicalDiagnosisStaffHospitalMismatchError,
    ClinicalDiagnosisStaffNotFoundError,
)
from app.modules.diagnoses.repositories import ClinicalDiagnosisRepository
from app.modules.diagnoses.schemas import (
    CreateClinicalDiagnosisRequest,
    ClinicalDiagnosisResponse,
)
from app.modules.diagnoses.services import ClinicalDiagnosisService
from app.modules.terminology.repositories import TerminologyRepository
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService
from app.modules.identity.permissions import Permissions
from app.modules.staff.repository import StaffRepository


router = APIRouter(
    prefix="/diagnoses",
    tags=["Clinical Diagnoses"],
)


def get_clinical_diagnosis_service(
    db: Session = Depends(get_db),
) -> ClinicalDiagnosisService:
    return ClinicalDiagnosisService(
        repository=ClinicalDiagnosisRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        terminology_repository=TerminologyRepository(db),
    )


@router.post(
    "",
    response_model=ClinicalDiagnosisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Clinical Diagnosis",
    dependencies=[
        Depends(require_permission(Permissions.DIAGNOSIS_CREATE)),
    ],
)
def create_clinical_diagnosis(
    request: CreateClinicalDiagnosisRequest,
    context: RequestContext = Depends(get_request_context),
    service: ClinicalDiagnosisService = Depends(
        get_clinical_diagnosis_service,
    ),
):
    try:
        diagnosis = service.create_diagnosis(
            context=context,
            encounter_id=request.encounter_id,
            diagnosis_name=request.diagnosis_name,
            code_system=request.code_system,
            code=request.code,
            diagnosis_type=request.diagnosis_type,
            certainty=request.certainty,
            onset_date=request.onset_date,
            notes=request.notes,
        )

        return ClinicalDiagnosisResponse.model_validate(diagnosis)

    except ClinicalDiagnosisEncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except ClinicalDiagnosisEncounterClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diagnoses cannot be recorded on a closed Encounter.",
        ) from exc

    except ClinicalDiagnosisEpisodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found.",
        ) from exc

    except ClinicalDiagnosisEpisodeClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diagnosis cannot be recorded on a closed Episode.",
        ) from exc

    except ClinicalDiagnosisEpisodeCancelledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diagnosis cannot be recorded on a cancelled Episode.",
        ) from exc

    except ClinicalDiagnosisStaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user does not have a Staff profile.",
        ) from exc

    except ClinicalDiagnosisStaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Staff member does not belong to the authenticated Hospital."
            ),
        ) from exc


@router.get(
    "/{diagnosis_id}",
    response_model=ClinicalDiagnosisResponse,
    summary="Retrieve Clinical Diagnosis",
    dependencies=[
        Depends(require_permission(Permissions.DIAGNOSIS_READ)),
    ],
)
def get_clinical_diagnosis(
    diagnosis_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: ClinicalDiagnosisService = Depends(
        get_clinical_diagnosis_service,
    ),
):
    try:
        diagnosis = service.get_diagnosis(
            context=context,
            diagnosis_id=diagnosis_id,
        )

        return ClinicalDiagnosisResponse.model_validate(diagnosis)

    except ClinicalDiagnosisNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical diagnosis not found.",
        ) from exc


@router.get(
    "/encounters/{encounter_id}",
    response_model=list[ClinicalDiagnosisResponse],
    summary="List Encounter Clinical Diagnoses",
    dependencies=[
        Depends(require_permission(Permissions.DIAGNOSIS_READ)),
    ],
)
def list_encounter_clinical_diagnoses(
    encounter_id: UUID,
    context: RequestContext = Depends(get_request_context),
    service: ClinicalDiagnosisService = Depends(
        get_clinical_diagnosis_service,
    ),
):
    try:
        diagnoses = service.list_encounter_diagnoses(
            context=context,
            encounter_id=encounter_id,
        )

        return [
            ClinicalDiagnosisResponse.model_validate(diagnosis)
            for diagnosis in diagnoses
        ]

    except ClinicalDiagnosisEncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc
