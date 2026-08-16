"""
==============================================================================
LIGHTBURGH EMR

Progress Note Schema
==============================================================================

Defines the structured content of a Progress Note Clinical Document.

The structure supports a SOAP-style clinical workflow without forcing the
clinician to use SOAP terminology in the user interface.
==============================================================================
"""

from pydantic import BaseModel, ConfigDict

from app.modules.clinical_documents.schemas.common import Assessment


class ProgressNoteContent(BaseModel):
    """
    Structured content for a Progress Note.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    subjective: str | None = None

    objective: str | None = None

    assessment: Assessment | None = None

    plan: str | None = None