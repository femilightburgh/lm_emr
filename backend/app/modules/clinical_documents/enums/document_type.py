"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Types
==============================================================================
"""

from enum import Enum


class ClinicalDocumentType(str, Enum):
    """
    Defines the types of clinical documents that can be recorded.
    """

    INITIAL_CLERKING = "INITIAL_CLERKING"

    PROGRESS_NOTE = "PROGRESS_NOTE"

    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"