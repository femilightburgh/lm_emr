"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Exceptions
==============================================================================
"""


class ClinicalOrderNotFoundError(Exception):
    """Raised when a Clinical Order cannot be found."""


class ClinicalOrderAlreadyCancelledError(Exception):
    """Raised when an already-cancelled order is cancelled again."""


class ClinicalOrderAlreadyCompletedError(Exception):
    """Raised when a completed order is cancelled."""


class ClinicalOrderEncounterClosedError(Exception):
    """Raised when an order is attempted on a closed Encounter."""


class ClinicalOrderEpisodeClosedError(Exception):
    """Raised when an order is attempted on a closed Episode."""


class ClinicalOrderEpisodeCancelledError(Exception):
    """Raised when an order is attempted on a cancelled Episode."""


class ClinicalOrderStaffNotFoundError(Exception):
    """Raised when the authenticated user has no Staff profile."""


class ClinicalOrderStaffHospitalMismatchError(Exception):
    """Raised when the Staff member belongs to another Hospital."""
