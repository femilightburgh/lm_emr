"""
==============================================================================
LIGHTBURGH EMR

Clinical Document API Request Schemas
==============================================================================

HTTP request schemas for Clinical Document operations.

Clinical content is validated according to the selected document type before
it reaches ClinicalDocumentService.

==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.modules.clinical_documents.enums import ClinicalDocumentType
from app.modules.clinical_documents.schemas import (
    get_document_content_schema,
)


# ============================================================================
# Create Document
# ============================================================================


class CreateClinicalDocumentRequest(BaseModel):
    """
    Request to create a Clinical Document draft.

    The document type determines which clinical-content schema is required.
    """

    encounter_id: UUID = Field(
        ...,
        description="Encounter in which the document is being created.",
    )

    document_type: ClinicalDocumentType = Field(
        ...,
        description="Type of Clinical Document being created.",
    )

    authored_by: UUID = Field(
        ...,
        description="Staff member authoring the document.",
    )

    content: dict = Field(
        ...,
        description="Structured clinical document content.",
    )

    @model_validator(mode="after")
    def validate_content_for_document_type(self):
        """
        Validate content against the schema registered for the selected
        document type.
        """

        schema = get_document_content_schema(
            self.document_type,
        )

        self.content = schema.model_validate(
            self.content,
        ).model_dump(
            mode="json",
        )

        return self


# ============================================================================
# Update Draft
# ============================================================================


class UpdateClinicalDocumentRequest(BaseModel):
    """
    Request to update an existing Clinical Document draft.

    Updating a draft modifies the existing document version.

    It does not create a new Clinical Document row and does not
    increment the version number.

    The original author of the document remains unchanged.

    The document type remains unchanged.

    Signed Clinical Documents cannot be updated.
    """

    edited_by: UUID = Field(
        ...,
        description="Staff member performing the draft update.",
    )

    content: dict = Field(
        ...,
        description="Updated structured clinical document content.",
    )


# ============================================================================
# Sign Document
# ============================================================================


class SignClinicalDocumentRequest(BaseModel):
    """
    Request to sign a Clinical Document.

    The signer is resolved from the authenticated UserAccount.
    The client does not supply a signed_by Staff ID.
    """

    signed_at: datetime | None = Field(
        default=None,
        description="Clinical signing time. Defaults to current UTC time.",
    )


# ============================================================================
# Amend Document
# ============================================================================


class AmendClinicalDocumentRequest(BaseModel):
    """
    Request to create a new draft version of a signed Clinical Document.

    The original signed document is never modified.
    """

    authored_by: UUID = Field(
        ...,
        description="Staff member authoring the amendment.",
    )

    content: dict = Field(
        ...,
        description="Updated structured clinical document content.",
    )