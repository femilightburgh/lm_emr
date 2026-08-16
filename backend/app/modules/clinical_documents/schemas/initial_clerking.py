"""
==============================================================================
LIGHTBURGH EMR

Initial Clerking Schema
==============================================================================

Defines the structured content of an Initial Clerking Clinical Document.

The schema reflects the major components of a traditional medical
clerking while allowing context-dependent sections to remain optional.

The resulting object is serialized into the ClinicalDocument.content JSON
field.
==============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field

from app.modules.clinical_documents.schemas.common import (
    Assessment,
    Examination,
    PatientPerspective,
    PresentingComplaint,
)


class InitialClerkingContent(BaseModel):
    """
    Structured content for an Initial Clerking document.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    # =========================================================================
    # History
    # =========================================================================

    presenting_complaints: list[PresentingComplaint] = Field(
        default_factory=list,
        description="Patient's presenting complaints.",
    )

    history_of_presenting_complaint: str | None = None

    review_of_systems: str | None = None

    past_medical_history: str | None = None

    past_surgical_history: str | None = None

    drug_history: str | None = None

    allergies: str | None = None

    family_history: str | None = None

    social_history: str | None = None

    personal_history: str | None = None

    # =========================================================================
    # Context-dependent History
    # =========================================================================

    gynaecological_history: str | None = None

    obstetric_history: str | None = None

    menstrual_history: str | None = None

    sexual_history: str | None = None

    # =========================================================================
    # Patient Perspective
    # =========================================================================

    patient_perspective: PatientPerspective | None = None

    # =========================================================================
    # Examination
    # =========================================================================

    examination: Examination | None = None

    # =========================================================================
    # Assessment
    # =========================================================================

    assessment: Assessment | None = None

    # =========================================================================
    # Investigations
    # =========================================================================

    investigations: list[str] = Field(
        default_factory=list,
        description="Investigations relevant to the clinical assessment.",
    )

    # =========================================================================
    # Plan
    # =========================================================================

    plan: str | None = None