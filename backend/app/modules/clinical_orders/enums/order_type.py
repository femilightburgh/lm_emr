"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Types
==============================================================================
"""

from enum import Enum


class ClinicalOrderType(str, Enum):
    """
    Domain types of Clinical Orders.
    """

    LABORATORY = "LABORATORY"
    RADIOLOGY = "RADIOLOGY"
    MEDICATION = "MEDICATION"
