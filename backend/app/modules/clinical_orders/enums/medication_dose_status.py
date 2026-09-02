"""
==============================================================================
LIGHTBURGH EMR

Medication Dose Statuses
==============================================================================
"""

from enum import Enum


class MedicationDoseStatus(str, Enum):
    """
    Lifecycle states of a scheduled inpatient medication dose.
    """

    PENDING = "PENDING"
    DUE = "DUE"
    GIVEN = "GIVEN"
    HELD = "HELD"
    MISSED = "MISSED"
    CANCELLED = "CANCELLED"
