"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Exceptions
==============================================================================

Domain exceptions raised by the Clinical Documents module.

These exceptions represent business-rule violations.

HTTP concerns belong in the API router.

==============================================================================
"""


class ClinicalDocumentError(Exception):
    """
    Base class for Clinical Document domain exceptions.
    """


class ClinicalDocumentNotFoundError(ClinicalDocumentError):
    """
    Raised when a Clinical Document cannot be found.
    """


class ClinicalDocumentNotLatestVersionError(ClinicalDocumentError):
    """
    Raised when an attempt is made to amend a Clinical Document
    that is not the latest version.
    """


class DocumentNotDraftError(ClinicalDocumentError):
    """
    Raised when an operation requires a DRAFT document.
    """


class DocumentNotSignedError(ClinicalDocumentError):
    """
    Raised when an operation requires a SIGNED document.
    """


class EncounterNotFoundError(ClinicalDocumentError):
    """
    Raised when the Encounter cannot be found.
    """


class EncounterClosedError(ClinicalDocumentError):
    """
    Raised when an operation attempts to create Clinical Documentation
    against a CLOSED Encounter.
    """


class EpisodeNotAdmittedError(ClinicalDocumentError):
    """
    Raised when a Discharge Summary is attempted for an Episode
    that has not been admitted.
    """


class NotManagingDoctorError(ClinicalDocumentError):
    """
    Raised when a clinician other than the Episode's managing doctor
    attempts to sign a Discharge Summary.
    """


class InvalidClinicalDocumentTypeError(ClinicalDocumentError):
    """
    Raised when an invalid Clinical Document type is supplied.
    """


class StaffNotFoundError(ClinicalDocumentError):
    """
    Raised when the specified staff member cannot be found.
    """


class StaffHospitalMismatchError(ClinicalDocumentError):
    """
    Raised when a staff member belongs to another Hospital.
    """


class InvalidClinicalDocumentContentError(ClinicalDocumentError):
    """
    Raised when Clinical Document content fails validation.
    """


class ClinicalDocumentAlreadySignedError(ClinicalDocumentError):
    """
    Raised when an already signed document is signed again.
    """