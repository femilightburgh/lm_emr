"""
==============================================================================
LIGHTBURGH EMR

Medication Nursing Summary Service
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
    MedicationDoseStatus,
)
from app.modules.clinical_orders.models import MedicationTreatment
from app.modules.clinical_orders.repositories import (
    MedicationTreatmentRepository,
)
from app.modules.clinical_orders.services.medication_round_service import (
    MedicationRoundService,
)
from app.modules.clinical_orders.services.medication_timing_policy import (
    classify_scheduled_dose,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)


class MedicationNursingSummaryService:
    """
    Builds the nurse-facing medication round and treatment summaries.
    """

    def __init__(
        self,
        *,
        treatment_repository: MedicationTreatmentRepository,
        episode_repository: EpisodeRepository,
    ) -> None:
        self.treatment_repository = treatment_repository
        self.episode_repository = episode_repository

    def build_episode_summary(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
        now: datetime | None = None,
    ) -> tuple[list[dict], dict]:
        """
        Return active prescription summaries and grouped medication rounds.
        """

        current_time = now or datetime.now(UTC)

        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=episode_id,
        )

        if episode is None:
            raise ValueError(
                "Episode not found."
            )

        if episode.status != EpisodeStatus.ADMITTED:
            raise ValueError(
                "Medication summary requires an admitted Episode."
            )

        treatments = (
            self.treatment_repository.list_active_by_episode(
                episode_id=episode_id,
            )
        )

        summaries: list[dict] = []

        all_doses = []
        dose_states: dict[UUID, str] = {}

        for treatment in treatments:
            prescription = treatment.prescription

            if prescription is None:
                continue

            given_count = 0
            held_count = 0
            missed_count = 0
            refused_count = 0
            remaining_count = 0

            pending_doses = []

            for dose in treatment.doses:
                administration = dose.administration

                scheduled_state = classify_scheduled_dose(
                    scheduled_at=dose.scheduled_at,
                    now=current_time,
                )

                if administration is not None:
                    if administration.status == (
                        MedicationAdministrationStatus.GIVEN
                    ):
                        given_count += 1

                    elif administration.status == (
                        MedicationAdministrationStatus.HELD
                    ):
                        held_count += 1

                    elif administration.status == (
                        MedicationAdministrationStatus.MISSED
                    ):
                        missed_count += 1

                    elif administration.status == (
                        MedicationAdministrationStatus.REFUSED
                    ):
                        refused_count += 1

                    all_doses.append(dose)
                    dose_states[dose.id] = scheduled_state

                    continue

                if dose.status == MedicationDoseStatus.CANCELLED:
                    continue

                state = classify_scheduled_dose(
                    scheduled_at=dose.scheduled_at,
                    now=current_time,
                )

                all_doses.append(dose)
                dose_states[dose.id] = state

                if state == "MISSED":
                    missed_count += 1
                    continue

                remaining_count += 1
                pending_doses.append(dose)

            next_dose = (
                min(
                    pending_doses,
                    key=lambda item: item.scheduled_at,
                )
                if pending_doses
                else None
            )

            summaries.append(
                {
                    "treatment_id": treatment.id,
                    "prescription_id": treatment.prescription_id,
                    "medicine_name": prescription.medicine_name,
                    "strength": prescription.strength,
                    "dose": prescription.dose,
                    "dose_unit": prescription.dose_unit,
                    "route": prescription.route,
                    "frequency": prescription.frequency,
                    "directions": prescription.directions,
                    "total_scheduled": (
                        given_count
                        + held_count
                        + missed_count
                        + refused_count
                        + remaining_count
                    ),
                    "given_count": given_count,
                    "held_count": held_count,
                    "missed_count": missed_count,
                    "refused_count": refused_count,
                    "remaining_count": remaining_count,
                    "next_dose_at": (
                        next_dose.scheduled_at
                        if next_dose is not None
                        else None
                    ),
                    "next_dose_state": (
                        dose_states[next_dose.id]
                        if next_dose is not None
                        else None
                    ),
                }
            )

        grouped_rounds = MedicationRoundService.group_doses(
            doses=all_doses,
        )

        current_round = None
        previous_round = None
        upcoming_rounds = []

        current_round_index = None

        for index, medication_round in enumerate(
            grouped_rounds,
        ):
            actionable_doses = [
                dose
                for dose in medication_round
                if dose.administration is None
                and dose_states[dose.id]
                in {
                    "DUE",
                    "OVERDUE",
                }
            ]

            if actionable_doses:
                current_round_index = index
                break

        if current_round_index is not None:
            current_round = self._round_payload(
                grouped_rounds[current_round_index],
                dose_states,
            )

            if current_round_index > 0:
                previous_round = self._round_payload(
                    grouped_rounds[current_round_index - 1],
                    dose_states,
                    outcomes_only=True,
                )

            for medication_round in grouped_rounds[
                current_round_index + 1:
            ]:
                earliest = min(
                    dose.scheduled_at
                    for dose in medication_round
                )

                if earliest > current_time:
                    upcoming_rounds.append(
                        self._round_payload(
                            medication_round,
                            dose_states,
                        )
                    )

        else:
            past_rounds = [
                medication_round
                for medication_round in grouped_rounds
                if max(
                    dose.scheduled_at
                    for dose in medication_round
                ) <= current_time
            ]

            if past_rounds:
                previous_round = self._round_payload(
                    past_rounds[-1],
                    dose_states,
                    outcomes_only=True,
                )

            upcoming_rounds = [
                self._round_payload(
                    medication_round,
                    dose_states,
                )
                for medication_round in grouped_rounds
                if min(
                    dose.scheduled_at
                    for dose in medication_round
                ) > current_time
            ]

        return summaries, {
            "current_round": current_round,
            "upcoming_rounds": upcoming_rounds,
            "previous_round": previous_round,
        }

    @staticmethod
    def _round_payload(
        medication_round,
        dose_states: dict[UUID, str],
        *,
        outcomes_only: bool = False,
    ) -> dict:
        """
        Convert one medication round into a nursing response payload.
        """

        doses = sorted(
            medication_round,
            key=lambda item: item.scheduled_at,
        )

        if outcomes_only:
            doses = [
                dose
                for dose in doses
                if dose.administration is not None
                and dose.administration.administered_at is not None
            ]

        return {
            "scheduled_at": min(
                dose.scheduled_at
                for dose in medication_round
            ),
            "doses": [
                MedicationNursingSummaryService._dose_payload(
                    treatment=dose.treatment,
                    dose=dose,
                    state=dose_states[dose.id],
                )
                for dose in doses
            ],
        }

    @staticmethod
    def _dose_payload(
        *,
        treatment: MedicationTreatment,
        dose,
        state: str,
    ) -> dict:
        prescription = treatment.prescription
        administration = dose.administration

        return {
            "id": dose.id,
            "treatment_id": treatment.id,
            "scheduled_at": dose.scheduled_at,
            "scheduled_state": state,
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
