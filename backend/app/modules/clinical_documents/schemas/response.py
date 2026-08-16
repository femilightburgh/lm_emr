"""
==============================================================================
LIGHTBURGH EMR

Clinical Document API Response Schemas
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)


class ClinicalDocumentResponse(BaseModel):
    """
    Response returned for a Clinical Document.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    encounter_id: UUID

    document_type: ClinicalDocumentType

    status: ClinicalDocumentStatus

    version: int

    content: dict

    authored_by: UUID

    signed_at: datetime | None

    signed_by: UUID | None

    amended_from_id: UUID | None