"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Exceptions
==============================================================================
"""


class EventNotFoundError(Exception):
    """Raised when a Clinical Event cannot be found."""


class EncounterNotFoundError(Exception):
    """Raised when the referenced Encounter does not exist."""


class EncounterHospitalMismatchError(Exception):
    """Raised when an Encounter belongs to another Hospital."""


class StaffNotFoundError(Exception):
    """Raised when the Event performer does not exist."""


class StaffHospitalMismatchError(Exception):
    """Raised when the Event performer belongs to another Hospital."""
    