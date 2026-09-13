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


class ClinicalOrderAlreadyInProgressError(Exception):
    """Raised when an already-in-progress order is started."""


class ClinicalOrderCannotStartError(Exception):
    """Raised when a Clinical Order cannot be started."""


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


class ClinicalOrderAlreadyReceivedError(Exception):
    """Raised when an already-received order is received again."""


class ClinicalOrderCannotReceiveError(Exception):
    """Raised when a Clinical Order cannot be received."""


class ClinicalOrderItemNotFoundError(Exception):
    """Raised when a Clinical Order Item cannot be found."""


class ClinicalOrderItemAlreadyReceivedError(Exception):
    """Raised when an already-received item is received again."""


class ClinicalOrderItemCannotReceiveError(Exception):
    """Raised when a Clinical Order Item cannot be received."""


class ClinicalOrderItemAlreadyInProgressError(Exception):
    """Raised when an already-in-progress item is started again."""


class ClinicalOrderItemAlreadyCompletedError(Exception):
    """Raised when a completed item is started again."""


class ClinicalOrderItemCannotStartError(Exception):
    """Raised when a Clinical Order Item cannot be started."""


class MedicationAdministrationStaffNotFoundError(Exception):
    """Raised when the authenticated user has no Staff profile."""


class MedicationAdministrationStaffHospitalMismatchError(Exception):
    """Raised when the Staff member belongs to another Hospital."""


class MedicationDoseNotFoundError(Exception):
    """Raised when a medication dose cannot be found."""


class MedicationDoseAlreadyAdministeredError(Exception):
    """Raised when a medication dose already has an administration record."""


class MedicationDoseCannotBeAdministeredError(Exception):
    """Raised when a medication dose is not eligible for administration."""


class MedicationAdministrationEpisodeError(Exception):
    """Raised when medication administration is attempted outside an admitted Episode."""
