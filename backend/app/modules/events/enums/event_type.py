"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Types
==============================================================================

Defines the types of clinical actions that can be recorded as Events.

An Event represents an action performed or recorded by a hospital
professional during an Encounter.
==============================================================================
"""

from enum import Enum


class EventType(str, Enum):
    """
    Defines the clinical actions that can be recorded as Clinical Events.
    """

    # ------------------------------------------------------------------
    # Clinical observations
    # ------------------------------------------------------------------

    VITALS_RECORDED = "VITALS_RECORDED"

    # ------------------------------------------------------------------
    # Clinical documentation
    # ------------------------------------------------------------------

    CLINICAL_NOTE_RECORDED = "CLINICAL_NOTE_RECORDED"

    # ------------------------------------------------------------------
    # Clinical assessment
    # ------------------------------------------------------------------

    DIAGNOSIS_RECORDED = "DIAGNOSIS_RECORDED"

    # ------------------------------------------------------------------
    # Medication
    # ------------------------------------------------------------------

    MEDICATION_PRESCRIBED = "MEDICATION_PRESCRIBED"

    MEDICATION_DISPENSED = "MEDICATION_DISPENSED"

    MEDICATION_GIVEN = "MEDICATION_GIVEN"

    # ------------------------------------------------------------------
    # Investigations
    # ------------------------------------------------------------------

    INVESTIGATION_ORDERED = "INVESTIGATION_ORDERED"

    CLINICAL_ORDER_CANCELLED = "CLINICAL_ORDER_CANCELLED"

    RESULT_RECORDED = "RESULT_RECORDED"

    # ------------------------------------------------------------------
    # Procedures
    # ------------------------------------------------------------------

    PROCEDURE_PERFORMED = "PROCEDURE_PERFORMED"

    WOUND_DRESSED = "WOUND_DRESSED"

    # ------------------------------------------------------------------
    # Episode lifecycle
    # ------------------------------------------------------------------

    EPISODE_ADMITTED = "EPISODE_ADMITTED"