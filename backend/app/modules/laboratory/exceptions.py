"""
==============================================================================
LIGHTBURGH EMR

Laboratory Catalogue Exceptions
==============================================================================
"""


class LaboratoryCatalogueError(Exception):
    """Base exception for laboratory catalogue business rules."""


class LaboratoryTestNotFoundError(LaboratoryCatalogueError):
    """Raised when a laboratory test cannot be found."""


class LaboratoryAnalyteNotFoundError(LaboratoryCatalogueError):
    """Raised when a laboratory analyte cannot be found."""


class LaboratoryAnalyteTestMismatchError(
    LaboratoryCatalogueError,
):
    """Raised when an analyte does not belong to the requested test."""


class LaboratoryReferenceRangeError(LaboratoryCatalogueError):
    """Raised when a laboratory reference range is invalid."""
