"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Schema Registry
==============================================================================

Maps each ClinicalDocumentType to the Pydantic schema responsible for
validating its clinical content.

The registry belongs to the application/API validation layer.

ClinicalDocumentService does not depend on this registry.
==============================================================================
"""

from typing import TypeAlias

from pydantic import BaseModel

from app.modules.clinical_documents.enums import ClinicalDocumentType

from app.modules.clinical_documents.schemas.discharge_summary import (
    DischargeSummaryContent,
)

from app.modules.clinical_documents.schemas.initial_clerking import (
    InitialClerkingContent,
)

from app.modules.clinical_documents.schemas.nursing_intake import (
    NursingIntakeContent,
)

from app.modules.clinical_documents.schemas.progress_note import (
    ProgressNoteContent,
)


ClinicalDocumentContentSchema: TypeAlias = type[BaseModel]


DOCUMENT_CONTENT_SCHEMAS: dict[
    ClinicalDocumentType,
    ClinicalDocumentContentSchema,
] = {
    ClinicalDocumentType.NURSING_INTAKE: NursingIntakeContent,

    ClinicalDocumentType.INITIAL_CLERKING: InitialClerkingContent,

    ClinicalDocumentType.PROGRESS_NOTE: ProgressNoteContent,

    ClinicalDocumentType.DISCHARGE_SUMMARY: DischargeSummaryContent,
}


def get_document_content_schema(
    document_type: ClinicalDocumentType,
) -> ClinicalDocumentContentSchema:
    """
    Return the Pydantic content schema for a Clinical Document type.
    """

    try:
        return DOCUMENT_CONTENT_SCHEMAS[document_type]

    except KeyError as exc:
        raise ValueError(
            f"No content schema registered for document type "
            f"'{document_type}'.",
        ) from exc