"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Exceptions
==============================================================================
"""


class ClinicalResultError(Exception):
    """Base exception for Clinical Result business rules."""


class ClinicalResultOrderNotFoundError(ClinicalResultError):
    """Raised when a Clinical Order cannot be found."""


class ClinicalResultOrderCancelledError(ClinicalResultError):
    """Raised when a result is recorded for a cancelled order."""


class ClinicalResultOrderAlreadyCompletedError(ClinicalResultError):
    """Raised when an already completed order is completed again."""


class ClinicalResultUnsupportedOrderTypeError(ClinicalResultError):
    """Raised when a result is recorded for a non-investigation order."""


class ClinicalResultStaffNotFoundError(ClinicalResultError):
    """Raised when the authenticated user has no Staff profile."""


class ClinicalResultStaffHospitalMismatchError(ClinicalResultError):
    """Raised when Staff belongs to another Hospital."""


class ClinicalResultLaboratoryTestNotFoundError(ClinicalResultError):
    """Raised when a laboratory order references an unknown test."""


class ClinicalResultUnknownAnalyteError(ClinicalResultError):
    """Raised when a result references an analyte not belonging to the test."""


class ClinicalResultDuplicateAnalyteError(ClinicalResultError):
    """Raised when an analyte is submitted more than once."""


class ClinicalResultInvalidValueError(ClinicalResultError):
    """Raised when an analyte value does not match its configured datatype."""


class ClinicalResultMissingRequiredAnalyteError(ClinicalResultError):
    """Raised when a required laboratory analyte is missing."""


class ClinicalResultNotFoundError(ClinicalResultError):
    """Raised when a Clinical Result cannot be found."""


class ClinicalResultAlreadyFinalError(ClinicalResultError):
    """Raised when a final Clinical Result is finalized again."""


class ClinicalResultOrderNotInProgressError(ClinicalResultError):
    """Raised when a result is finalized for a non-active order."""
