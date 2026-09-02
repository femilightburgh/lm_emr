"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Exceptions
==============================================================================
"""


class DiagnosticError(Exception):
    """
    Base exception for diagnostic domain errors.
    """


class DiagnosticInvestigationNotFoundError(DiagnosticError):
    """
    Raised when a diagnostic investigation cannot be found.
    """


class DiagnosticReportNotFoundError(DiagnosticError):
    """
    Raised when a diagnostic report cannot be found.
    """


class DiagnosticReportAlreadyExistsError(DiagnosticError):
    """
    Raised when a diagnostic report already exists for an order.
    """


class DiagnosticReportFinalizedError(DiagnosticError):
    """
    Raised when an operation is attempted on a finalized report.
    """


class DiagnosticCategoryMismatchError(DiagnosticError):
    """
    Raised when a report category does not match its investigation.
    """


class DiagnosticReportOrderNotInProgressError(DiagnosticError):
    """
    Raised when a diagnostic report is created before the order is started.
    """


class DiagnosticReportOrderCancelledError(DiagnosticError):
    """
    Raised when a diagnostic report operation targets a cancelled order.
    """


class DiagnosticReportOrderNotFoundError(DiagnosticError):
    """
    Raised when the clinical order associated with a diagnostic report
    cannot be found.
    """


class DiagnosticReportStaffNotFoundError(DiagnosticError):
    """
    Raised when the authenticated user has no Staff profile.
    """


class DiagnosticReportStaffHospitalMismatchError(DiagnosticError):
    """
    Raised when the authenticated Staff belongs to another hospital.
    """
