"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Status
==============================================================================
"""

from enum import Enum


class ClinicalDocumentStatus(str, Enum):
    """
    Lifecycle status of a Clinical Document version.

    A signed version is immutable.

    Amendments create a new document version rather than modifying
    an existing signed version.
    """

    DRAFT = "DRAFT"

    SIGNED = "SIGNED"