"""
LIGHTBURGH EMR

Encounter Exceptions

==============================================================================

Business exceptions raised by the Encounter domain.

==============================================================================
"""


class EncounterError(Exception):
    """Base exception for Encounter business errors."""


class EncounterNotFoundError(EncounterError):
    """Raised when an Encounter cannot be found."""


class EpisodeNotFoundError(EncounterError):
    """Raised when the referenced Episode cannot be found."""


class EpisodeNotOpenError(EncounterError):
    """Raised when an Encounter is attempted on a non-open Episode."""


class StaffNotFoundError(EncounterError):
    """Raised when the referenced Staff member cannot be found."""


class StaffHospitalMismatchError(EncounterError):
    """Raised when Staff belongs to a different Hospital."""

class EncounterAlreadyClosedError(EncounterError):
    """Raised when an already closed Encounter is closed again."""