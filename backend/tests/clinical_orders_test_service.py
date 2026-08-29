"""
==============================================================================
LIGHTBURGH EMR

Clinical Order Service Tests
==============================================================================
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.context import RequestContext
from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount
from app.modules.clinical_orders.enums import ClinicalOrderType
from app.modules.clinical_orders.exceptions import (
    ClinicalOrderEncounterClosedError,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    PrescriptionRepository,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
)
from app.modules.encounter.models import EncounterStatus
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import EpisodeService
from app.modules.events.enums import EventType
from app.modules.events.models import ClinicalEvent
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)
from app.modules.patients.services.patient_service import (
    PatientService,
)
from app.modules.staff.employment_repository import (
    StaffEmploymentRepository,
)
from app.modules.staff.enums import (
    EmploymentStatus,
    EmploymentType,
    Gender,
    Profession,
)
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import StaffCreate
from app.modules.staff.service import StaffService
from app.modules.organization.repository import HospitalRepository


def create_test_context(
    hospital,
) -> RequestContext:
    return RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )


def create_test_encounter(
    db,
    hospital,
):
    user = UserAccount(
        hospital_id=hospital.id,
        email=f"staff-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    patient = PatientService(
        repository=PatientRepository(db),
    ).create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=f"PAT-ORDER-{uuid4().hex[:8]}",
            first_name="Order",
            last_name="Patient",
            sex="Male",
            date_of_birth=datetime(1990, 1, 1).date(),
        ),
    )

    staff = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    ).create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STF-ORDER-{uuid4().hex[:8]}",
            first_name="Ordering",
            last_name="Clinician",
            gender=Gender.MALE,
            date_of_birth=datetime(1985, 1, 1).date(),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=datetime(2026, 1, 1).date(),
        )
    )

    staff.user_account_id = user.id
    db.flush()

    episode_repository = EpisodeRepository(db)

    episode = EpisodeService(
        repository=episode_repository,
        patient_repository=PatientRepository(db),
        number_generator=EpisodeNumberGenerator(
            repository=episode_repository,
        ),
        encounter_repository=EncounterRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
    ).create_episode(
        context=context,
        patient_id=patient.id,
        title="Clinical Order Test Episode",
    )

    encounter = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    ).create_encounter(
        context=context,
        episode_id=episode.id,
        staff_id=staff.id,
        title="Doctor Consultation",
    )

    return context, staff, episode, encounter


def create_order_service(db):
    return ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
    )


def test_create_laboratory_order_creates_investigation_event(
    db,
    hospital,
):
    context, staff, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
    )

    assert order.id is not None
    assert order.encounter_id == encounter.id
    assert order.ordered_by == staff.id
    assert order.order_type == ClinicalOrderType.LABORATORY
    assert order.status.value == "REQUESTED"

    event = db.query(ClinicalEvent).filter(
        ClinicalEvent.encounter_id == encounter.id,
        ClinicalEvent.event_type == EventType.INVESTIGATION_ORDERED,
    ).one()

    assert event.performed_by == staff.id
    assert event.payload["clinical_order_id"] == str(order.id)
    assert event.payload["order_type"] == "LABORATORY"


def test_create_medication_order_creates_prescription_event(
    db,
    hospital,
):
    context, staff, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    medicine_id = str(uuid4())

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.MEDICATION,
        priority="URGENT",
        details={
            "medication_id": medicine_id,
            "medicine_name": "Amoxicillin",
            "strength": "500 mg",
            "dose": "500",
            "dose_unit": "mg",
            "route": "ORAL",
            "frequency": "TDS",
            "duration": "5",
            "duration_unit": "days",
            "quantity": "15 capsules",
            "directions": "Take after food.",
            "indication": "Bacterial infection.",
        },
    )

    assert order.order_type == ClinicalOrderType.MEDICATION

    prescription = PrescriptionRepository(
        db,
    ).get_by_order_id(
        order_id=order.id,
    )

    assert prescription is not None
    assert prescription.clinical_order_id == order.id
    assert prescription.medicine_name == "Amoxicillin"
    assert prescription.strength == "500 mg"
    assert prescription.dose == "500"
    assert prescription.dose_unit == "mg"
    assert prescription.route == "ORAL"
    assert prescription.frequency == "TDS"
    assert prescription.duration == "5"
    assert prescription.duration_unit == "days"
    assert prescription.quantity == "15 capsules"
    assert prescription.directions == "Take after food."
    assert prescription.indication == "Bacterial infection."

    event = db.query(ClinicalEvent).filter(
        ClinicalEvent.encounter_id == encounter.id,
        ClinicalEvent.event_type == EventType.MEDICATION_PRESCRIBED,
    ).one()

    assert event.performed_by == staff.id
    assert event.payload["clinical_order_id"] == str(order.id)


def test_create_order_rejects_closed_encounter(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    encounter.status = EncounterStatus.CLOSED
    encounter.ended_at = datetime.now(timezone.utc)
    db.commit()

    service = create_order_service(db)

    with pytest.raises(ClinicalOrderEncounterClosedError):
        service.create_order(
            context=context,
            encounter_id=encounter.id,
            order_type=ClinicalOrderType.RADIOLOGY,
            priority="ROUTINE",
            details={
                "study_code": "CXR",
                "study_name": "Chest X-ray",
            },
        )


def test_create_order_rejects_cancelled_episode(
    db,
    hospital,
):
    context, _, episode, encounter = create_test_encounter(
        db,
        hospital,
    )

    from app.modules.episode.models import EpisodeStatus

    episode.status = EpisodeStatus.CANCELLED
    db.commit()

    service = create_order_service(db)

    from app.modules.clinical_orders.exceptions import (
        ClinicalOrderEpisodeCancelledError,
    )

    with pytest.raises(ClinicalOrderEpisodeCancelledError):
        service.create_order(
            context=context,
            encounter_id=encounter.id,
            order_type=ClinicalOrderType.LABORATORY,
            priority="ROUTINE",
            details={"test_code": "CBC"},
        )


def test_create_order_rejects_closed_episode(
    db,
    hospital,
):
    context, _, episode, encounter = create_test_encounter(
        db,
        hospital,
    )

    from app.modules.episode.models import EpisodeStatus

    episode.status = EpisodeStatus.CLOSED
    db.commit()

    service = create_order_service(db)

    from app.modules.clinical_orders.exceptions import (
        ClinicalOrderEpisodeClosedError,
    )

    with pytest.raises(ClinicalOrderEpisodeClosedError):
        service.create_order(
            context=context,
            encounter_id=encounter.id,
            order_type=ClinicalOrderType.RADIOLOGY,
            priority="ROUTINE",
            details={"study_code": "CXR"},
        )


def test_create_order_rejects_user_without_staff_profile(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    from app.modules.identity.models import UserAccount
    from app.modules.identity.enums import AccountStatus
    from app.modules.clinical_orders.exceptions import (
        ClinicalOrderStaffNotFoundError,
    )

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"orphan-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.commit()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = create_order_service(db)

    with pytest.raises(ClinicalOrderStaffNotFoundError):
        service.create_order(
            context=context,
            encounter_id=encounter.id,
            order_type=ClinicalOrderType.LABORATORY,
            priority="ROUTINE",
            details={"test_code": "CBC"},
        )


def test_create_order_rejects_invalid_order_type(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    with pytest.raises(ValueError):
        service.create_order(
            context=context,
            encounter_id=encounter.id,
            order_type="INVALID",
            priority="ROUTINE",
            details={"test_code": "CBC"},
        )


def test_cancel_order_creates_cancellation_event(
    db,
    hospital,
):
    context, staff, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={"test_code": "CBC"},
    )

    cancelled = service.cancel_order(
        context=context,
        order_id=order.id,
    )

    assert cancelled.status.value == "CANCELLED"
    assert cancelled.cancelled_at is not None

    event = db.query(ClinicalEvent).filter(
        ClinicalEvent.encounter_id == encounter.id,
        ClinicalEvent.event_type == EventType.CLINICAL_ORDER_CANCELLED,
    ).one()

    assert event.performed_by == staff.id
    assert event.payload["clinical_order_id"] == str(order.id)


def test_cancel_completed_order_is_rejected(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.MEDICATION,
        priority="ROUTINE",
        details={"medication_id": str(uuid4())},
    )

    from app.modules.clinical_orders.enums import ClinicalOrderStatus
    from app.modules.clinical_orders.exceptions import (
        ClinicalOrderAlreadyCompletedError,
    )

    order.status = ClinicalOrderStatus.COMPLETED
    db.commit()

    with pytest.raises(ClinicalOrderAlreadyCompletedError):
        service.cancel_order(
            context=context,
            order_id=order.id,
        )


def test_cancel_order_cannot_be_cancelled_twice(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.RADIOLOGY,
        priority="ROUTINE",
        details={"study_code": "CXR"},
    )

    service.cancel_order(
        context=context,
        order_id=order.id,
    )

    from app.modules.clinical_orders.exceptions import (
        ClinicalOrderAlreadyCancelledError,
    )

    with pytest.raises(ClinicalOrderAlreadyCancelledError):
        service.cancel_order(
            context=context,
            order_id=order.id,
        )


def test_get_order_returns_order_within_hospital(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={"test_code": "CBC"},
    )

    retrieved = service.get_order(
        context=context,
        order_id=order.id,
    )

    assert retrieved.id == order.id
    assert retrieved.encounter_id == encounter.id


def test_list_encounter_orders_returns_orders_in_order(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_order_service(db)

    first = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={"test_code": "CBC"},
    )

    second = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.RADIOLOGY,
        priority="ROUTINE",
        details={"study_code": "CXR"},
    )

    orders = service.list_encounter_orders(
        context=context,
        encounter_id=encounter.id,
    )

    assert [item.id for item in orders] == [
        first.id,
        second.id,
    ]
