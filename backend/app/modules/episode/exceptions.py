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