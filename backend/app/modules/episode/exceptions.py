"""
==============================================================================
LIGHTBURGH EMR

Episode Exceptions

==============================================================================

Domain exceptions raised by the Episode module.

These exceptions represent business rule violations.

HTTP concerns belong in the router.

==============================================================================
"""


class EpisodeError(Exception):
    """
    Base class for Episode domain exceptions.
    """


class EpisodeAlreadyExistsError(EpisodeError):
    """
    Raised when an Episode number already exists.
    """


class EpisodeNotFoundError(EpisodeError):
    """
    Raised when an Episode cannot be found.
    """


class PatientNotFoundError(EpisodeError):
    """
    Raised when the specified Patient does not exist.
    """


class EpisodeAlreadyClosedError(EpisodeError):
    """
    Raised when an already closed Episode is modified.
    """


class EpisodeAlreadyCancelledError(EpisodeError):
    """
    Raised when an already cancelled Episode is modified.
    """


class EpisodeAlreadyAdmittedError(EpisodeError):
    """
    Raised when an already admitted Episode is admitted again
    or an operation is attempted that is not permitted for an
    admitted Episode.
    """


class EpisodeNotOpenError(EpisodeError):
    """
    Raised when an operation requires an Episode to be OPEN.
    """


class EncounterNotBelongingToEpisodeError(EpisodeError):
    """
    Raised when an Encounter does not belong to the Episode
    being modified.
    """


class EncounterNotOpenError(EpisodeError):
    """
    Raised when an operation requires an OPEN Encounter.
    """


class StaffNotFoundError(EpisodeError):
    """
    Raised when the admission clinician cannot be found.
    """


class StaffHospitalMismatchError(EpisodeError):
    """
    Raised when the admission clinician belongs to another hospital.
    """


class StaffNotDoctorError(EpisodeError):
    """
    Raised when a non-doctor attempts to become the managing doctor.
    """