"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Common Schemas
==============================================================================

Reusable structured components shared by Clinical Document types.

These schemas provide structure at the application layer while the
ClinicalDocument model continues to persist the final document content
as JSON.
==============================================================================
"""

from pydantic import BaseModel, Field


# ============================================================================
# Presenting Complaint
# ============================================================================


class PresentingComplaint(BaseModel):
    """
    A single presenting complaint and its duration.
    """

    complaint: str = Field(
        ...,
        min_length=1,
        description="The patient's presenting complaint.",
    )

    duration: str = Field(
        ...,
        min_length=1,
        description="Duration of the presenting complaint.",
    )


# ============================================================================
# Patient Perspective
# ============================================================================


class PatientPerspective(BaseModel):
    """
    ICE-style patient perspective.

    Ideas:
        What the patient thinks is happening.

    Concerns:
        What worries the patient.

    Expectations:
        What the patient hopes will happen.
    """

    ideas: str | None = None

    concerns: str | None = None

    expectations: str | None = None


# ============================================================================
# Examination
# ============================================================================


class Examination(BaseModel):
    """
    Narrative physical examination findings.

    Examination findings are deliberately narrative rather than broken
    into rigid individual measurements. Structured measurements such as
    vital signs belong to the Vitals/Event system.
    """

    general: str | None = None

    cardiovascular: str | None = None

    respiratory: str | None = None

    abdomen: str | None = None

    neurological: str | None = None

    musculoskeletal: str | None = None

    genitourinary: str | None = None

    other: str | None = None


# ============================================================================
# Assessment
# ============================================================================


class Assessment(BaseModel):
    """
    Clinical assessment following history and examination.
    """

    working_diagnosis: str | None = None

    differentials: list[str] = Field(
        default_factory=list,
    )