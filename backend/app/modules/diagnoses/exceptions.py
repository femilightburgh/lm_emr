class ClinicalDiagnosisError(Exception):
    """Base exception for Clinical Diagnosis operations."""


class ClinicalDiagnosisNotFoundError(ClinicalDiagnosisError):
    """Raised when a diagnosis cannot be found."""


class ClinicalDiagnosisStaffNotFoundError(ClinicalDiagnosisError):
    """Raised when the authenticated user has no Staff profile."""


class ClinicalDiagnosisStaffHospitalMismatchError(ClinicalDiagnosisError):
    """Raised when authenticated Staff belongs to another hospital."""


class ClinicalDiagnosisEncounterNotFoundError(ClinicalDiagnosisError):
    """Raised when the target encounter does not exist."""


class ClinicalDiagnosisEncounterClosedError(ClinicalDiagnosisError):
    """Raised when the target encounter is closed."""


class ClinicalDiagnosisEpisodeNotFoundError(ClinicalDiagnosisError):
    """Raised when the target episode does not exist."""


class ClinicalDiagnosisEpisodeClosedError(ClinicalDiagnosisError):
    """Raised when the target episode is closed."""


class ClinicalDiagnosisEpisodeCancelledError(ClinicalDiagnosisError):
    """Raised when the target episode is cancelled."""
