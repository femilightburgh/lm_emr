"""
==============================================================================
LIGHTBURGH EMR

Inpatient Medication Treatment Schemas
==============================================================================
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
    MedicationDoseStatus,
    MedicationTreatmentStatus,
)


class MedicationDoseResponse(BaseModel):
    """
    Scheduled inpatient medication dose response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    treatment_id: UUID
    scheduled_at: datetime
    status: MedicationDoseStatus


class MedicationTreatmentResponse(BaseModel):
    """
    Inpatient medication treatment response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    prescription_id: UUID
    episode_id: UUID
    status: MedicationTreatmentStatus
    start_at: datetime
    end_at: datetime | None
    discontinued_at: datetime | None
    discontinued_by: UUID | None
    discontinued_reason: str | None
    doses: list[MedicationDoseResponse]


class MedicationAdministrationResponse(BaseModel):
    """
    Recorded nursing outcome for a scheduled medication dose.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    dose_id: UUID
    administered_by: UUID
    status: MedicationAdministrationStatus
    administered_at: datetime | None
    dose_given: str | None
    reason: str | None
    notes: str | None


class MedicationDoseQueueResponse(BaseModel):
    """
    Medication dose task presented to Nursing.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    treatment_id: UUID
    scheduled_at: datetime
    status: MedicationDoseStatus

    treatment_status: MedicationTreatmentStatus

    medicine_name: str
    strength: str | None
    dose: str
    dose_unit: str | None
    route: str
    frequency: str

    duration: str | None
    duration_unit: str | None
    directions: str | None

    administration: MedicationAdministrationResponse | None = None


class MedicationNursingDoseResponse(BaseModel):
    """
    Nursing-facing scheduled medication dose.
    """

    id: UUID
    treatment_id: UUID
    scheduled_at: datetime

    scheduled_state: str
    administration_status: str | None
    administration_at: datetime | None
    dose_given: str | None
    reason: str | None
    notes: str | None

    medicine_name: str
    strength: str | None
    dose: str
    dose_unit: str | None
    route: str
    frequency: str
    directions: str | None


class MedicationPrescriptionSummaryResponse(BaseModel):
    """
    Nursing-facing summary of an active medication treatment.
    """

    treatment_id: UUID
    prescription_id: UUID

    medicine_name: str
    strength: str | None
    dose: str
    dose_unit: str | None
    route: str
    frequency: str
    directions: str | None

    total_scheduled: int
    given_count: int
    held_count: int
    missed_count: int
    refused_count: int
    remaining_count: int

    next_dose_at: datetime | None
    next_dose_state: str | None


class MedicationTreatmentHistoryResponse(BaseModel):
    """
    Complete medication history for one inpatient treatment.
    """

    treatment: MedicationPrescriptionSummaryResponse
    doses: list[MedicationNursingDoseResponse]


class MedicationNursingRoundGroupResponse(BaseModel):
    """
    A group of medication doses belonging to one nursing round.
    """

    scheduled_at: datetime
    doses: list[MedicationNursingDoseResponse]


class MedicationNursingRoundResponse(BaseModel):
    """
    Medication round grouped for inpatient Nursing.
    """

    current_round: MedicationNursingRoundGroupResponse | None

    upcoming_rounds: list[
        MedicationNursingRoundGroupResponse
    ]

    previous_round: MedicationNursingRoundGroupResponse | None


class MedicationNursingSummaryResponse(BaseModel):
    """
    Complete inpatient Nursing medication view.
    """

    prescriptions: list[
        MedicationPrescriptionSummaryResponse
    ]

    round: MedicationNursingRoundResponse
