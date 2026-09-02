"""
==============================================================================
LIGHTBURGH EMR

Medication Administration Statuses
==============================================================================
"""

from enum import Enum


class MedicationAdministrationStatus(str, Enum):
    """
    Status of an inpatient medication administration record.
    """

    GIVEN = "GIVEN"
    HELD = "HELD"
    MISSED = "MISSED"
    REFUSED = "REFUSED"
