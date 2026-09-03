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


# ============================================================================
# Episode existence / lifecycle
# ============================================================================


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


# ============================================================================
# Encounter
# ============================================================================


class EncounterNotBelongingToEpisodeError(EpisodeError):
    """
    Raised when an Encounter does not belong to the Episode
    being modified.
    """


class EncounterNotOpenError(EpisodeError):
    """
    Raised when an operation requires an OPEN Encounter.
    """

class InvalidConsultationDispositionError(EpisodeError):
    """
    Raised when a Doctor Consultation disposition is not supported
    by the current Episode workflow.
    """


class DoctorReviewEncounterRequiredError(EpisodeError):
    """
    Raised when an operation requires a Doctor Review Encounter.
    """


class InvalidWardReviewDispositionError(EpisodeError):
    """
    Raised when a Ward Review disposition is invalid.
    """


class WardReviewEncounterRequiredError(EpisodeError):
    """
    Raised when an operation requires a Ward Review Encounter.
    """


class WardReviewDispositionDetailsRequiredError(EpisodeError):
    """
    Raised when a Ward Review disposition requires additional details.
    """


# ============================================================================
# Staff
# ============================================================================


class StaffNotFoundError(EpisodeError):
    """
    Raised when a required Staff profile cannot be found.
    """


class StaffHospitalMismatchError(EpisodeError):
    """
    Raised when a Staff member belongs to another hospital.
    """


class StaffNotDoctorError(EpisodeError):
    """
    Raised when a non-doctor attempts to become the managing doctor.
    """


# ============================================================================
# Reception workflow
# ============================================================================


class EpisodeAlreadyCheckedInError(EpisodeError):
    """
    Raised when an Episode that has already been checked in
    is checked in again.
    """


class EpisodeNotAwaitingCheckInError(EpisodeError):
    """
    Raised when an operation requires an Episode to be awaiting
    receptionist check-in.
    """


# ============================================================================
# Nursing workflow
# ============================================================================


class EpisodeAlreadyInNursingError(EpisodeError):
    """
    Raised when an Episode is already being handled by nursing.
    """


class EpisodeNotWaitingForNursingError(EpisodeError):
    """
    Raised when an operation requires an Episode to be waiting
    for nursing.
    """


class EpisodeNotInNursingError(EpisodeError):
    """
    Raised when an operation requires an Episode to be in
    nursing intake.
    """


# ============================================================================
# Routing
# ============================================================================


class EpisodeAlreadyRoutedError(EpisodeError):
    """
    Raised when an Episode has already been routed.
    """


class DepartmentNotFoundError(EpisodeError):
    """
    Raised when the target Department cannot be found.
    """


class DepartmentHospitalMismatchError(EpisodeError):
    """
    Raised when the target Department belongs to another hospital.
    """


class DepartmentInactiveError(EpisodeError):
    """
    Raised when an inactive Department is selected for routing.
    """

class NursingIntakeNotSignedError(EpisodeError):
    """
    Raised when an Episode is routed before the latest Nursing Intake
    Clinical Document has been signed.
    """