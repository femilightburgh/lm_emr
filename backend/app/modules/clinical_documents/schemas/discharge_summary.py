"""
==============================================================================
LIGHTBURGH EMR

Discharge Summary Schema
==============================================================================

Defines the structured content of a Discharge Summary Clinical Document.
==============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field


class DischargeSummaryContent(BaseModel):
    """
    Structured content for a Discharge Summary.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    admission_summary: str | None = None

    hospital_course: str | None = None

    diagnoses: list[str] = Field(
        default_factory=list,
    )

    procedures: list[str] = Field(
        default_factory=list,
    )

    investigations: list[str] = Field(
        default_factory=list,
    )

    discharge_medications: list[str] = Field(
        default_factory=list,
    )

    condition_at_discharge: str | None = None

    follow_up_plan: str | None = None