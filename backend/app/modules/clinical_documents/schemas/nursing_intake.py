"""
==============================================================================
LIGHTBURGH EMR

Nursing Intake Clinical Document
==============================================================================

Defines the structured clinical content recorded by nursing staff during
initial patient intake.

This document belongs to a Nursing Encounter.

Vitals are deliberately NOT duplicated here.

Vitals are recorded through the Vitals module as Clinical Events.

The Nursing Intake document captures the nurse's clinical assessment,
observations, and relevant history.
==============================================================================
"""

from pydantic import BaseModel, Field


class NursingIntakeContent(BaseModel):
    """
    Structured content for a Nursing Intake document.
    """

    # ------------------------------------------------------------------
    # Presenting Information
    # ------------------------------------------------------------------

    presenting_complaint: str | None = Field(
        default=None,
        max_length=2000,
        description="Patient's presenting complaint as reported at intake.",
    )

    history_of_presenting_complaint: str | None = Field(
        default=None,
        max_length=5000,
        description="Brief history of the presenting complaint.",
    )

    # ------------------------------------------------------------------
    # Allergies
    # ------------------------------------------------------------------

    known_allergies: list[str] = Field(
        default_factory=list,
        description="Known drug, food, or environmental allergies.",
    )

    allergy_notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Additional allergy information.",
    )

    # ------------------------------------------------------------------
    # Relevant History
    # ------------------------------------------------------------------

    past_medical_history: str | None = Field(
        default=None,
        max_length=5000,
        description="Relevant past medical history.",
    )

    current_medications: list[str] = Field(
        default_factory=list,
        description="Medications currently being taken by the patient.",
    )

    surgical_history: str | None = Field(
        default=None,
        max_length=3000,
        description="Relevant previous surgical history.",
    )

    # ------------------------------------------------------------------
    # Nursing Assessment
    # ------------------------------------------------------------------

    general_appearance: str | None = Field(
        default=None,
        max_length=2000,
        description="General appearance and overall clinical impression.",
    )

    level_of_consciousness: str | None = Field(
        default=None,
        max_length=500,
        description="Observed level of consciousness.",
    )

    mobility_status: str | None = Field(
        default=None,
        max_length=500,
        description="Patient mobility or mobility limitation.",
    )

    pain_score: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Pain score from 0 to 10.",
    )

    pain_location: str | None = Field(
        default=None,
        max_length=1000,
        description="Location of reported pain.",
    )

    # ------------------------------------------------------------------
    # Safety / Risk
    # ------------------------------------------------------------------

    fall_risk: str | None = Field(
        default=None,
        max_length=500,
        description="Nursing assessment of fall risk.",
    )

    pressure_injury_risk: str | None = Field(
        default=None,
        max_length=500,
        description="Nursing assessment of pressure injury risk.",
    )

    infection_precautions: str | None = Field(
        default=None,
        max_length=1000,
        description="Any infection-control precautions identified.",
    )

    # ------------------------------------------------------------------
    # Nursing Observations
    # ------------------------------------------------------------------

    nursing_observations: str | None = Field(
        default=None,
        max_length=5000,
        description="Additional nursing observations.",
    )

    immediate_concerns: str | None = Field(
        default=None,
        max_length=3000,
        description="Immediate concerns requiring clinician attention.",
    )

    # ------------------------------------------------------------------
    # Handover
    # ------------------------------------------------------------------

    handover_notes: str | None = Field(
        default=None,
        max_length=5000,
        description="Information relevant to handover to the next clinician.",
    )