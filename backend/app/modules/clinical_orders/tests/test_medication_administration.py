"""
==============================================================================
LIGHTBURGH EMR

Medication Administration Tests
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import app.models

from sqlalchemy import select

from app.core.context import RequestContext
from app.db.session import SessionLocal

from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
    MedicationDoseStatus,
    MedicationTreatmentStatus,
)
from app.modules.clinical_orders.exceptions import (
    MedicationDoseCannotBeAdministeredError,
)

from app.modules.clinical_orders.models import (
    MedicationAdministration,
    MedicationDose,
    MedicationTreatment,
)
from app.modules.clinical_orders.repositories import (
    MedicationAdministrationRepository,
    MedicationTreatmentRepository,
)
from app.modules.clinical_orders.services import (
    MedicationAdministrationService,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.staff.models import Staff
from app.modules.staff.repository import (
    StaffRepository,
)


HOSPITAL_ID = UUID(
    "f46b4674-ecf3-4f03-b0cf-a1ff5ba6a409"
)


def build_service(db) -> MedicationAdministrationService:
    return MedicationAdministrationService(
        repository=MedicationAdministrationRepository(db),
        treatment_repository=MedicationTreatmentRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )


def get_test_staff_user_id(db) -> UUID:
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

    return staff_user_id


def get_pending_dose(
    db,
    *,
    future: bool = False,
) -> MedicationDose:
    dose = db.execute(
        select(MedicationDose)
        .join(
            MedicationDose.treatment,
        )
        .where(
            MedicationTreatment.episode_id.is_not(None),
            MedicationTreatment.status
            == MedicationTreatmentStatus.ACTIVE,
            MedicationDose.status == MedicationDoseStatus.PENDING,
            ~MedicationDose.administration.has(),
        )
        .order_by(
            MedicationDose.scheduled_at,
        )
        .limit(1)
    ).scalar_one_or_none()

    assert dose is not None

    now = datetime.now(UTC)

    if future:
        dose.scheduled_at = now + timedelta(hours=1)
    else:
        dose.scheduled_at = now - timedelta(minutes=1)

    db.flush()

    return dose


def build_context(
    staff_user_id: UUID,
) -> RequestContext:
    return RequestContext(
        user_id=staff_user_id,
        hospital_id=HOSPITAL_ID,
        permissions=frozenset(),
    )


def test_given_records_administration_and_updates_dose():
    with SessionLocal() as db:
        dose = get_pending_dose(db)
        staff_user_id = get_test_staff_user_id(db)

        service = build_service(db)

        try:
            administration = service.record_administration(
                context=build_context(staff_user_id),
                dose_id=dose.id,
                status=MedicationAdministrationStatus.GIVEN,
                administered_at=datetime.now(UTC),
                dose_given="500 mg",
                notes="Patient tolerated dose.",
            )

            assert administration.dose_id == dose.id
            assert (
                administration.status
                == MedicationAdministrationStatus.GIVEN
            )
            staff = db.execute(
                select(Staff)
                .where(
                    Staff.user_account_id == staff_user_id,
                    Staff.hospital_id == HOSPITAL_ID,
                )
            ).scalar_one()

            assert (
                administration.administered_by
                == staff.id
            )
            assert (
                administration.dose_given == "500 mg"
            )
            assert (
                administration.notes
                == "Patient tolerated dose."
            )

            db.refresh(dose)

            assert (
                dose.status
                == MedicationDoseStatus.GIVEN
            )
            assert administration.id is not None

        finally:
            db.rollback()


def test_held_records_reason_and_updates_dose():
    with SessionLocal() as db:
        dose = get_pending_dose(db)
        staff_user_id = get_test_staff_user_id(db)

        service = build_service(db)

        try:
            administration = service.record_administration(
                context=build_context(staff_user_id),
                dose_id=dose.id,
                status=MedicationAdministrationStatus.HELD,
                reason="Blood pressure below hold parameter.",
            )

            assert (
                administration.status
                == MedicationAdministrationStatus.HELD
            )
            assert (
                administration.reason
                == "Blood pressure below hold parameter."
            )

            db.refresh(dose)

            assert (
                dose.status
                == MedicationDoseStatus.HELD
            )

        finally:
            db.rollback()


def test_refused_records_refusal_without_invalid_dose_mapping():
    with SessionLocal() as db:
        dose = get_pending_dose(db)
        staff_user_id = get_test_staff_user_id(db)

        service = build_service(db)

        original_status = dose.status

        try:
            administration = service.record_administration(
                context=build_context(staff_user_id),
                dose_id=dose.id,
                status=MedicationAdministrationStatus.REFUSED,
                reason="Patient refused medication.",
            )

            assert (
                administration.status
                == MedicationAdministrationStatus.REFUSED
            )
            assert (
                administration.reason
                == "Patient refused medication."
            )

            db.refresh(dose)

            assert dose.status == original_status

        finally:
            db.rollback()



def test_future_scheduled_dose_is_rejected():
    with SessionLocal() as db:
        dose = get_pending_dose(
            db,
            future=True,
        )
        staff_user_id = get_test_staff_user_id(db)

        service = build_service(db)

        try:
            try:
                service.record_administration(
                    context=build_context(staff_user_id),
                    dose_id=dose.id,
                    status=MedicationAdministrationStatus.GIVEN,
                )
            except MedicationDoseCannotBeAdministeredError as exc:
                assert (
                    "scheduled time"
                    in str(exc).lower()
                )
            else:
                raise AssertionError(
                    "Expected a future scheduled dose "
                    "to be rejected."
                )

        finally:
            db.rollback()


def test_duplicate_administration_is_rejected():
    with SessionLocal() as db:
        dose = get_pending_dose(db)
        staff_user_id = get_test_staff_user_id(db)

        service = build_service(db)

        try:
            service.record_administration(
                context=build_context(staff_user_id),
                dose_id=dose.id,
                status=MedicationAdministrationStatus.GIVEN,
            )

            try:
                service.record_administration(
                    context=build_context(staff_user_id),
                    dose_id=dose.id,
                    status=MedicationAdministrationStatus.GIVEN,
                )
            except Exception as exc:
                assert (
                    "already been administered"
                    in str(exc)
                )
            else:
                raise AssertionError(
                    "Expected duplicate administration to fail."
                )

        finally:
            db.rollback()


def test_cancelled_dose_is_rejected():
    with SessionLocal() as db:
        dose = get_pending_dose(db)
        staff_user_id = get_test_staff_user_id(db)

        service = build_service(db)

        try:
            dose.status = MedicationDoseStatus.CANCELLED
            db.flush()

            try:
                service.record_administration(
                    context=build_context(staff_user_id),
                    dose_id=dose.id,
                    status=MedicationAdministrationStatus.GIVEN,
                )
            except Exception as exc:
                assert (
                    "Cancelled medication doses"
                    in str(exc)
                )
            else:
                raise AssertionError(
                    "Expected cancelled dose to be rejected."
                )

        finally:
            db.rollback()
