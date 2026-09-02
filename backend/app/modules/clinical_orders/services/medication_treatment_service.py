"""
==============================================================================
LIGHTBURGH EMR

Inpatient Medication Treatment Service
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import (
    ClinicalOrderType,
    MedicationFrequency,
)
from app.modules.clinical_orders.models import (
    MedicationDose,
    MedicationDoseStatus,
    MedicationTreatment,
    MedicationTreatmentStatus,
    Prescription,
)
from app.modules.clinical_orders.repositories import (
    MedicationTreatmentRepository,
)
from app.modules.clinical_orders.services.medication_scheduler import (
    generate_schedule,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)


class InpatientMedicationService:
    """
    Creates and manages inpatient medication treatments.
    """

    def __init__(
        self,
        *,
        db: Session,
        episode_repository: EpisodeRepository,
        treatment_repository: MedicationTreatmentRepository,
    ) -> None:
        self.db = db
        self.episode_repository = episode_repository
        self.treatment_repository = treatment_repository

    def create_treatment(
        self,
        *,
        context: RequestContext,
        prescription: Prescription,
        start_at: datetime | None = None,
        first_dose_at: datetime | None = None,
    ) -> MedicationTreatment:
        """
        Create an inpatient treatment and its initial dose schedule.
        """

        if prescription.clinical_order is None:
            raise ValueError(
                "Prescription clinical order could not be resolved.",
            )

        order = prescription.clinical_order

        if order.order_type != ClinicalOrderType.MEDICATION:
            raise ValueError(
                "Prescription must belong to a medication order.",
            )

        encounter = order.encounter

        if encounter is None:
            raise ValueError(
                "Prescription encounter could not be resolved.",
            )

        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=encounter.episode_id,
        )

        if episode is None:
            raise ValueError(
                "Episode not found.",
            )

        if episode.status != EpisodeStatus.ADMITTED:
            raise ValueError(
                "Medication treatment requires an admitted Episode.",
            )

        existing = (
            self.treatment_repository.get_by_prescription_id(
                prescription_id=prescription.id,
            )
        )

        if existing is not None:
            raise ValueError(
                "Medication treatment already exists.",
            )

        treatment_start = (
            start_at
            if start_at is not None
            else datetime.now(UTC)
        )

        if treatment_start.tzinfo is None:
            raise ValueError(
                "Treatment start time must include a timezone.",
            )

        effective_first_dose = (
            first_dose_at
            if first_dose_at is not None
            else treatment_start
        )

        if effective_first_dose.tzinfo is None:
            raise ValueError(
                "First dose time must include a timezone.",
            )

        if effective_first_dose < treatment_start:
            raise ValueError(
                "First dose cannot occur before treatment starts.",
            )

        end_at = self._calculate_end_at(
            start_at=treatment_start,
            prescription=prescription,
        )

        frequency = self._parse_frequency(
            prescription.frequency,
        )

        treatment = MedicationTreatment(
            prescription_id=prescription.id,
            episode_id=episode.id,
            status=MedicationTreatmentStatus.ACTIVE,
            start_at=treatment_start,
            end_at=end_at,
        )

        self.treatment_repository.create(
            treatment=treatment,
        )

        self.treatment_repository.flush()

        scheduled_times = generate_schedule(
            start_at=treatment_start,
            first_dose_at=effective_first_dose,
            frequency=frequency,
            end_at=end_at,
        )

        for scheduled_at in scheduled_times:
            self.db.add(
                MedicationDose(
                    treatment_id=treatment.id,
                    scheduled_at=scheduled_at,
                    status=MedicationDoseStatus.PENDING,
                )
            )

        self.db.flush()

        return treatment

    def _parse_frequency(
        self,
        frequency: str,
    ) -> MedicationFrequency:
        normalized = frequency.strip().upper()

        try:
            return MedicationFrequency(
                normalized,
            )
        except ValueError as exc:
            raise ValueError(
                f"Unsupported inpatient medication frequency: "
                f"{frequency}"
            ) from exc

    def _calculate_end_at(
        self,
        *,
        start_at: datetime,
        prescription: Prescription,
    ) -> datetime | None:
        if (
            prescription.duration is None
            or prescription.duration_unit is None
        ):
            return None

        try:
            duration = float(
                prescription.duration,
            )
        except ValueError as exc:
            raise ValueError(
                "Medication duration must be numeric "
                "for inpatient scheduling.",
            ) from exc

        unit = (
            prescription.duration_unit
            .strip()
            .lower()
        )

        if unit in (
            "minute",
            "minutes",
            "min",
            "mins",
        ):
            return start_at + timedelta(
                minutes=duration,
            )

        if unit in (
            "hour",
            "hours",
            "hr",
            "hrs",
        ):
            return start_at + timedelta(
                hours=duration,
            )

        if unit in (
            "day",
            "days",
            "d",
        ):
            return start_at + timedelta(
                days=duration,
            )

        raise ValueError(
            f"Unsupported medication duration unit: "
            f"{prescription.duration_unit}"
        )
