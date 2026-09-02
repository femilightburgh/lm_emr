"""
==============================================================================
LIGHTBURGH EMR

Medication Treatment Statuses
==============================================================================
"""

from enum import Enum


class MedicationTreatmentStatus(str, Enum):
    """
    Lifecycle states of an inpatient medication treatment.
    """

    ACTIVE = "ACTIVE"
    DISCONTINUED = "DISCONTINUED"
    COMPLETED = "COMPLETED"
