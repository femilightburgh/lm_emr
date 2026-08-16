"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Schemas
==============================================================================

Public schema exports for the Clinical Documents module.

==============================================================================
"""

from app.modules.clinical_documents.schemas.common import (
    Assessment,
    Examination,
    PatientPerspective,
    PresentingComplaint,
)

from app.modules.clinical_documents.schemas.discharge_summary import (
    DischargeSummaryContent,
)

from app.modules.clinical_documents.schemas.initial_clerking import (
    InitialClerkingContent,
)

from app.modules.clinical_documents.schemas.progress_note import (
    ProgressNoteContent,
)

from app.modules.clinical_documents.schemas.registry import (
    DOCUMENT_CONTENT_SCHEMAS,
    ClinicalDocumentContentSchema,
    get_document_content_schema,
)

from app.modules.clinical_documents.schemas.request import (
    AmendClinicalDocumentRequest,
    CreateClinicalDocumentRequest,
    SignClinicalDocumentRequest,
    UpdateClinicalDocumentRequest,
)

from app.modules.clinical_documents.schemas.response import (
    ClinicalDocumentResponse,
)


__all__ = [
    # ------------------------------------------------------------------
    # Common Clinical Content Schemas
    # ------------------------------------------------------------------
    "PresentingComplaint",
    "PatientPerspective",
    "Examination",
    "Assessment",

    # ------------------------------------------------------------------
    # Document Content Schemas
    # ------------------------------------------------------------------
    "DischargeSummaryContent",
    "InitialClerkingContent",
    "ProgressNoteContent",

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------
    "ClinicalDocumentContentSchema",
    "DOCUMENT_CONTENT_SCHEMAS",
    "get_document_content_schema",

    # ------------------------------------------------------------------
    # Request Schemas
    # ------------------------------------------------------------------
    "CreateClinicalDocumentRequest",
    "UpdateClinicalDocumentRequest",
    "SignClinicalDocumentRequest",
    "AmendClinicalDocumentRequest",

    # ------------------------------------------------------------------
    # Response Schemas
    # ------------------------------------------------------------------
    "ClinicalDocumentResponse",
]