"""
==============================================================================
LIGHTBURGH EMR

Reception Schemas
==============================================================================
"""

from pydantic import BaseModel


class ReceptionOverviewResponse(BaseModel):
    """
    Hospital-wide operational summary for Reception.
    """

    total_patients: int
    currently_admitted: int
    checked_in_today: int

    waiting_for_nursing: int
    nursing_in_progress: int
    routed: int
    awaiting_investigations: int
    awaiting_review: int
