"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Statuses
==============================================================================
"""

from enum import Enum


class ClinicalOrderStatus(str, Enum):
    """
    Lifecycle states of a Clinical Order.
    """

    REQUESTED = "REQUESTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
