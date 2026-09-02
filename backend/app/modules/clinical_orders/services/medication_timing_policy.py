"""
==============================================================================
LIGHTBURGH EMR

Medication Timing Policy
==============================================================================
"""

from datetime import timedelta


DUE_WINDOW_MINUTES = 10
MISSED_AFTER_MINUTES = 90

DUE_WINDOW = timedelta(
    minutes=DUE_WINDOW_MINUTES,
)

MISSED_AFTER = timedelta(
    minutes=MISSED_AFTER_MINUTES,
)


def classify_scheduled_dose(
    *,
    scheduled_at,
    now,
) -> str:
    """
    Classify an unadministered scheduled dose for Nursing.
    """

    delta = now - scheduled_at

    if delta < -DUE_WINDOW:
        return "UPCOMING"

    if delta <= DUE_WINDOW:
        return "DUE"

    if delta <= MISSED_AFTER:
        return "OVERDUE"

    return "MISSED"
