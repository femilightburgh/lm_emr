"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Types
==============================================================================
"""

from enum import Enum


class ClinicalResultType(str, Enum):
    """
    Type of clinical result being recorded.
    """

    LABORATORY = "LABORATORY"
    RADIOLOGY = "RADIOLOGY"
