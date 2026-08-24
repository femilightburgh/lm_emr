"""
==============================================================================
LIGHTBURGH EMR

Clinical Document API Router
==============================================================================

HTTP endpoints for Clinical Documents.

Business logic belongs in ClinicalDocumentService.

Database access belongs in repositories.

==============================================================================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.db.session import get_db

from app.modules.clinical_documents.exceptions import (
    ClinicalDocumentNotFoundError,
    ClinicalDocumentNotLatestVersionError,
    DocumentNotDraftError,
    DocumentNotSignedError,
    EncounterClosedError,
    EncounterNotFoundError,
    EpisodeNotAdmittedError,
    NotManagingDoctorError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)

from app.modules.clinical_documents.repositories import (
    ClinicalDocumentRepository,
)

from app.modules.clinical_documents.schemas import (
    AmendClinicalDocumentRequest,
    ClinicalDocumentResponse,
    CreateClinicalDocumentRequest,
    UpdateClinicalDocumentRequest,
    get_document_content_schema,
)

from app.modules.clinical_documents.services.clinical_document_service import (
    ClinicalDocumentService,
)

from app.modules.events.repositories import (
    ClinicalEventRepository,
)

from app.modules.events.services.event_service import (
    ClinicalEventService,
)


router = APIRouter(
    prefix="/clinical-documents",
    tags=["Clinical Documents"],
)


# ============================================================================
# Dependencies
# ============================================================================


def get_clinical_document_service(
    db: Session = Depends(get_db),
) -> ClinicalDocumentService:
    """
    Build the ClinicalDocumentService dependency graph.
    """

    return ClinicalDocumentService(
        repository=ClinicalDocumentRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
    )


# ============================================================================
# Create
# ============================================================================


@router.post(
    "",
    response_model=ClinicalDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Clinical Document Draft",
)
def create_clinical_document(
    request: CreateClinicalDocumentRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalDocumentService = Depends(
        get_clinical_document_service,
    ),
):
    """
    Create a Clinical Document in DRAFT status.
    """

    try:
        document = service.create_draft(
            context=context,
            encounter_id=request.encounter_id,
            document_type=request.document_type,
            authored_by=request.authored_by,
            content=request.content,
        )

        return ClinicalDocumentResponse.model_validate(
            document,
        )

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc

    except EncounterClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Clinical Documents cannot be created on a closed Encounter."
            ),
        ) from exc

    except EpisodeNotAdmittedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A Discharge Summary requires an admitted Episode."
            ),
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Staff member does not belong to the authenticated Hospital."
            ),
        ) from exc


# ============================================================================
# Retrieve
# ============================================================================


@router.get(
    "/{document_id}",
    response_model=ClinicalDocumentResponse,
    summary="Retrieve a Clinical Document",
)
def get_clinical_document(
    document_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalDocumentService = Depends(
        get_clinical_document_service,
    ),
):
    """
    Retrieve a Clinical Document.
    """

    try:
        document = service.get_document(
            context=context,
            document_id=document_id,
        )

        return ClinicalDocumentResponse.model_validate(
            document,
        )

    except ClinicalDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Document not found.",
        ) from exc


# ============================================================================
# Encounter Documents
# ============================================================================


@router.get(
    "/encounters/{encounter_id}",
    response_model=list[ClinicalDocumentResponse],
    summary="List Clinical Documents for an Encounter",
)
def list_encounter_documents(
    encounter_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalDocumentService = Depends(
        get_clinical_document_service,
    ),
):
    """
    List Clinical Documents belonging to an Encounter.
    """

    try:
        documents = service.list_encounter_documents(
            context=context,
            encounter_id=encounter_id,
        )

        return [
            ClinicalDocumentResponse.model_validate(
                document,
            )
            for document in documents
        ]

    except EncounterNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found.",
        ) from exc


# ============================================================================
# Update Draft
# ============================================================================


@router.patch(
    "/{document_id}",
    response_model=ClinicalDocumentResponse,
    summary="Update a Clinical Document Draft",
)
def update_clinical_document(
    document_id: UUID,
    request: UpdateClinicalDocumentRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalDocumentService = Depends(
        get_clinical_document_service,
    ),
):
    """
    Update a DRAFT Clinical Document.
    """

    try:
        existing_document = service.get_document(
            context=context,
            document_id=document_id,
        )

        schema = get_document_content_schema(
            existing_document.document_type,
        )

        validated_content = schema.model_validate(
            request.content,
        ).model_dump(
            mode="json",
        )

        document = service.update_draft(
            context=context,
            document_id=document_id,
            edited_by=request.edited_by,
            content=validated_content,
        )

        return ClinicalDocumentResponse.model_validate(
            document,
        )

    except ClinicalDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Document not found.",
        ) from exc

    except DocumentNotDraftError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft Clinical Documents can be edited.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Staff member does not belong to the authenticated Hospital."
            ),
        ) from exc


# ============================================================================
# Sign
# ============================================================================


@router.post(
    "/{document_id}/sign",
    response_model=ClinicalDocumentResponse,
    summary="Sign a Clinical Document",
)
def sign_clinical_document(
    document_id: UUID,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalDocumentService = Depends(
        get_clinical_document_service,
    ),
):
    """
    Sign a DRAFT Clinical Document.

    For DISCHARGE_SUMMARY documents, only the Episode managing
    doctor may sign.
    """

    try:
        document = service.sign_document(
            context=context,
            document_id=document_id,
            signed_at=None,
        )

        return ClinicalDocumentResponse.model_validate(
            document,
        )

    except ClinicalDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Document not found.",
        ) from exc

    except DocumentNotDraftError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft Clinical Documents can be signed.",
        ) from exc

    except EpisodeNotAdmittedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A Discharge Summary can only be signed for an admitted Episode."
            ),
        ) from exc

    except NotManagingDoctorError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the Episode managing doctor can sign the Discharge Summary."
            ),
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Staff member does not belong to the authenticated Hospital."
            ),
        ) from exc


# ============================================================================
# Amend
# ============================================================================


@router.post(
    "/{document_id}/amend",
    response_model=ClinicalDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Amend a Clinical Document",
)
def amend_clinical_document(
    document_id: UUID,
    request: AmendClinicalDocumentRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
    service: ClinicalDocumentService = Depends(
        get_clinical_document_service,
    ),
):
    """
    Create a new DRAFT version from a SIGNED Clinical Document.

    Only the latest version may be amended.
    """

    try:
        existing_document = service.get_document(
            context=context,
            document_id=document_id,
        )

        schema = get_document_content_schema(
            existing_document.document_type,
        )

        validated_content = schema.model_validate(
            request.content,
        ).model_dump(
            mode="json",
        )

        document = service.amend_document(
            context=context,
            document_id=document_id,
            authored_by=request.authored_by,
            content=validated_content,
        )

        return ClinicalDocumentResponse.model_validate(
            document,
        )

    except ClinicalDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical Document not found.",
        ) from exc

    except ClinicalDocumentNotLatestVersionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only the latest Clinical Document version can be amended."
            ),
        ) from exc

    except DocumentNotSignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only signed Clinical Documents can be amended.",
        ) from exc

    except StaffNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found.",
        ) from exc

    except StaffHospitalMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Staff member does not belong to the authenticated Hospital."
            ),
        ) from exc