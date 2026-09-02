"""
==============================================================================
LIGHTBURGH EMR

Inpatient Medication Atomicity Tests
==============================================================================
"""

from datetime import datetime, UTC
from uuid import UUID

import app.models

from sqlalchemy import select

from app.core.context import RequestContext
from app.db.session import SessionLocal

from app.modules.clinical_orders.enums import (
    ClinicalOrderType,
)
from app.modules.clinical_orders.models import (
    ClinicalOrder,
    MedicationDose,
    MedicationTreatment,
    Prescription,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    MedicationTreatmentRepository,
    PrescriptionRepository,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
    InpatientMedicationService,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.staff.models import Staff
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services import (
    ClinicalEventService,
)
from app.modules.staff.repository import (
    StaffRepository,
)


HOSPITAL_ID = UUID(
    "f46b4674-ecf3-4f03-b0cf-a1ff5ba6a409"
)

ENCOUNTER_ID = UUID(
    "aee9eed1-be58-467f-9614-ec47d91b3e59"
)


def build_service(db) -> ClinicalOrderService:
    return ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )


def test_inpatient_medication_failure_rolls_back_order_and_prescription():
    with SessionLocal() as db:
        staff_user_id = db.execute(
            select(
                Staff.user_account_id,
            )
            .where(
                Staff.hospital_id == HOSPITAL_ID,
                Staff.user_account_id.is_not(None),
            )
            .limit(1)
        ).scalar_one_or_none()

        assert staff_user_id is not None

        context = RequestContext(
            user_id=staff_user_id,
            hospital_id=HOSPITAL_ID,
            permissions=frozenset(),
        )

        service = build_service(db)

        before_orders = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(ClinicalOrder.id),
            )
        )

        before_prescriptions = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(Prescription.id),
            )
        )

        before_treatments = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(MedicationTreatment.id),
            )
        )

        before_doses = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(MedicationDose.id),
            )
        )

        try:
            service.create_order(
                context=context,
                encounter_id=ENCOUNTER_ID,
                order_type=ClinicalOrderType.MEDICATION,
                priority="ROUTINE",
                details={
                    "medicine_name": "Atomicity Test Medication",
                    "strength": "500 mg",
                    "dose": "500",
                    "dose_unit": "mg",
                    "route": "ORAL",
                    "frequency": "INVALID_FREQUENCY",
                    "duration": "2",
                    "duration_unit": "days",
                    "quantity": "6",
                    "directions": None,
                    "indication": "Atomicity test",
                },
                start_at=datetime.now(UTC),
                first_dose_at=datetime.now(UTC),
            )

        except ValueError as exc:
            assert (
                "Unsupported inpatient medication frequency"
                in str(exc)
            )

        else:
            raise AssertionError(
                "Expected inpatient medication creation to fail."
            )

        after_orders = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(ClinicalOrder.id),
            )
        )

        after_prescriptions = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(Prescription.id),
            )
        )

        after_treatments = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(MedicationTreatment.id),
            )
        )

        after_doses = db.scalar(
            select(
                __import__(
                    "sqlalchemy",
                    fromlist=["func"],
                ).func.count(MedicationDose.id),
            )
        )

        assert after_orders == before_orders
        assert after_prescriptions == before_prescriptions
        assert after_treatments == before_treatments
        assert after_doses == before_doses
