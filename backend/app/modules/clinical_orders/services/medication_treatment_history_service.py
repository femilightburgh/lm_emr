"""
==============================================================================
LIGHTBURGH EMR

Medication Treatment History Service
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
    MedicationDoseStatus,
)
from app.modules.clinical_orders.repositories import (
    MedicationTreatmentRepository,
)
from app.modules.clinical_orders.services.medication_timing_policy import (
    classify_scheduled_dose,
)


class MedicationTreatmentHistoryService:
    """
    Builds the complete medication history for one inpatient treatment.
    """

    def __init__(
        self,
        *,
        treatment_repository: MedicationTreatmentRepository,
    ) -> None:
        self.treatment_repository = treatment_repository

    def build_history(
        self,
        *,
        context: RequestContext,
        treatment_id: UUID,
        now: datetime | None = None,
    ) -> dict:
        current_time = now or datetime.now(UTC)

        treatment = self.treatment_repository.get_by_id(
            treatment_id=treatment_id,
        )

        if treatment is None:
            raise ValueError(
                "Medication treatment not found."
            )

        if treatment.episode is None:
            raise ValueError(
                "Medication treatment Episode could not be resolved."
            )

        if treatment.episode.hospital_id != context.hospital_id:
            raise ValueError(
                "Medication treatment does not belong to the authenticated Hospital."
            )

        prescription = treatment.prescription

        if prescription is None:
            raise ValueError(
                "Medication prescription could not be resolved."
            )

        doses = []

        for dose in treatment.doses:
            if dose.status == MedicationDoseStatus.CANCELLED:
                continue

            scheduled_state = classify_scheduled_dose(
                scheduled_at=dose.scheduled_at,
                now=current_time,
            )

            administration = dose.administration

            doses.append(
                {
                    "id": dose.id,
                    "treatment_id": treatment.id,
                    "scheduled_at": dose.scheduled_at,
                    "scheduled_state": scheduled_state,
                    "administration_status": (
                        administration.status.value
                        if administration is not None
                        else None
                    ),
                    "administration_at": (
                        administration.administered_at
                        if administration is not None
                        else None
                    ),
                    "dose_given": (
                        administration.dose_given
                        if administration is not None
                        else None
                    ),
                    "reason": (
                        administration.reason
                        if administration is not None
                        else None
                    ),
                    "notes": (
                        administration.notes
                        if administration is not None
                        else None
                    ),
                    "medicine_name": prescription.medicine_name,
                    "strength": prescription.strength,
                    "dose": prescription.dose,
                    "dose_unit": prescription.dose_unit,
                    "route": prescription.route,
                    "frequency": prescription.frequency,
                    "directions": prescription.directions,
                }
            )

        return {
            "treatment": {
                "treatment_id": treatment.id,
                "prescription_id": treatment.prescription_id,
                "medicine_name": prescription.medicine_name,
                "strength": prescription.strength,
                "dose": prescription.dose,
                "dose_unit": prescription.dose_unit,
                "route": prescription.route,
                "frequency": prescription.frequency,
                "directions": prescription.directions,
                "total_scheduled": len(treatment.doses),
                "given_count": sum(
                    dose["administration_status"] == (
                        MedicationAdministrationStatus.GIVEN.value
                    )
                    for dose in doses
                ),
                "held_count": sum(
                    dose["administration_status"] == (
                        MedicationAdministrationStatus.HELD.value
                    )
                    for dose in doses
                ),
                "missed_count": sum(
                    dose["administration_status"] == (
                        MedicationAdministrationStatus.MISSED.value
                    )
                    for dose in doses
                ),
                "refused_count": sum(
                    dose["administration_status"] == (
                        MedicationAdministrationStatus.REFUSED.value
                    )
                    for dose in doses
                ),
                "remaining_count": sum(
                    dose["administration_status"] is None
                    and dose["scheduled_state"] != "MISSED"
                    for dose in doses
                ),
                "next_dose_at": next(
                    (
                        dose["scheduled_at"]
                        for dose in doses
                        if dose["administration_status"] is None
                        and dose["scheduled_state"] != "MISSED"
                    ),
                    None,
                ),
                "next_dose_state": next(
                    (
                        dose["scheduled_state"]
                        for dose in doses
                        if dose["administration_status"] is None
                        and dose["scheduled_state"] != "MISSED"
                    ),
                    None,
                ),
            },
            "doses": sorted(
                doses,
                key=lambda item: item["scheduled_at"],
                reverse=True,
            ),
        }
