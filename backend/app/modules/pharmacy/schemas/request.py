"""
==============================================================================
LIGHTBURGH EMR

Pharmacy Request Schemas
==============================================================================
"""

from pydantic import BaseModel, Field


class DispensePrescriptionRequest(BaseModel):
    """
    Request to dispense a medication prescription.
    """

    quantity_dispensed: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    notes: str | None = None
