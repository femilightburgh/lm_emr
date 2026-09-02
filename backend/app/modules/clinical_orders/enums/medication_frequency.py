"""
==============================================================================
LIGHTBURGH EMR

Medication Frequency
==============================================================================
"""

from enum import Enum


class MedicationFrequency(str, Enum):
    """
    Supported inpatient medication scheduling frequencies.
    """

    STAT = "STAT"
    ONCE = "ONCE"

    Q2H = "Q2H"
    Q4H = "Q4H"
    Q6H = "Q6H"
    Q8H = "Q8H"
    Q12H = "Q12H"
    Q24H = "Q24H"

    BID = "BID"
    TDS = "TDS"
    QID = "QID"
