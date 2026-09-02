"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Categories
==============================================================================
"""

from enum import Enum


class DiagnosticCategory(str, Enum):
    """
    Categories of diagnostic investigations.
    """

    RADIOLOGY = "RADIOLOGY"
    CARDIOLOGY = "CARDIOLOGY"
    NEUROPHYSIOLOGY = "NEUROPHYSIOLOGY"
    RESPIRATORY = "RESPIRATORY"
    AUDIOLOGY = "AUDIOLOGY"
    ENDOSCOPY = "ENDOSCOPY"
