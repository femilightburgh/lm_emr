"""
==============================================================================
LIGHTBURGH EMR

Prescription API Tests
==============================================================================
"""

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app

from app.modules.clinical_orders.models import (
    Prescription,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.models import ClinicalEvent
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService
from app.modules.clinical_orders.services import ClinicalOrderService
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.pharmacy.repositories import (
    DispensingRepository,
)
from app.modules.pharmacy.services import (
    DispensingService,
)
from app.modules.clinical_orders.repositories import (
    PrescriptionRepository,
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
from app.modules.identity.repository import IdentityRepository

@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


from tests.clinical_orders.test_router import (
    auth_headers,
    authenticate,
    create_doctor_encounter,
    create_hospital,
    create_user,
)

def test_doctor_can_create_structured_prescription(
    client,
    db: Session,
):
    hospital = create_hospital(db)

    doctor = create_user(
        db,
        hospital=hospital,
        email=f"prescriber-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=doctor.email,
    )

    response = client.post(
        "/api/v1/prescriptions",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "priority": "ROUTINE",
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

    assert response.status_code == 201

    body = response.json()

    assert body["medicine_name"] == "Amoxicillin"
    assert body["strength"] == "500 mg"
    assert body["dose"] == "500"
    assert body["dose_unit"] == "mg"
    assert body["route"] == "ORAL"
    assert body["frequency"] == "TDS"
    assert body["duration"] == "5"
    assert body["duration_unit"] == "days"
    assert body["quantity"] == "15 capsules"
    assert body["directions"] == "Take after food."
    assert body["indication"] == "Bacterial infection."

    prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == body["id"],
        )
        .one()
    )

    assert prescription.clinical_order_id is not None
    assert prescription.medicine_name == "Amoxicillin"
    assert prescription.route == "ORAL"
    assert prescription.frequency == "TDS"


def test_pharmacy_queue_returns_structured_prescription(
    client,
    db: Session,
):
    hospital = create_hospital(db)

    doctor = create_user(
        db,
        hospital=hospital,
        email=f"queue-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=doctor.email,
    )

    create_response = client.post(
        "/api/v1/prescriptions",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "priority": "URGENT",
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

    assert create_response.status_code == 201

    queue_response = client.get(
        "/api/v1/prescriptions/queue",
        headers=auth_headers(token),
    )

    assert queue_response.status_code == 200

    queue = queue_response.json()

    matching = next(
        item
        for item in queue
        if item["prescription_id"]
        == create_response.json()["id"]
    )

    assert matching["medicine_name"] == "Amoxicillin"
    assert matching["strength"] == "500 mg"
    assert matching["dose"] == "500"
    assert matching["dose_unit"] == "mg"
    assert matching["route"] == "ORAL"
    assert matching["frequency"] == "TDS"
    assert matching["duration"] == "5"
    assert matching["duration_unit"] == "days"
    assert matching["quantity"] == "15 capsules"
    assert matching["directions"] == "Take after food."
    assert matching["indication"] == "Bacterial infection."
    assert matching["status"] == "REQUESTED"
    assert matching["priority"] == "URGENT"


def test_pharmacist_can_receive_and_start_prescription(
    client,
    db: Session,
):
    hospital = create_hospital(db)

    doctor = create_user(
        db,
        hospital=hospital,
        email=f"lifecycle-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    pharmacist = create_user(
        db,
        hospital=hospital,
        email=f"pharmacist-{uuid4()}@example.com",
        role_name="Pharmacist",
    )

    pharmacist_staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=__import__(
            "app.modules.organization.repository",
            fromlist=["HospitalRepository"],
        ).HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    pharmacist_staff = pharmacist_staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STAFF-PHAR-{uuid4().hex[:8]}",
            first_name="Pharmacy",
            last_name="Tester",
            gender=Gender.FEMALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.PHARMACIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        ),
    )

    pharmacist_staff_service.link_user_account(
        pharmacist_staff.id,
        pharmacist.id,
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor,
    )

    doctor_token = authenticate(
        db,
        hospital=hospital,
        email=doctor.email,
    )

    create_response = client.post(
        "/api/v1/prescriptions",
        headers=auth_headers(doctor_token),
        json={
            "encounter_id": str(encounter.id),
            "priority": "ROUTINE",
            "medicine_name": "Paracetamol",
            "strength": "500 mg",
            "dose": "500",
            "dose_unit": "mg",
            "route": "ORAL",
            "frequency": "QID",
            "duration": "3",
            "duration_unit": "days",
            "quantity": "12 tablets",
            "directions": "Take after food.",
            "indication": "Fever.",
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["clinical_order_id"]

    pharmacist_token = authenticate(
        db,
        hospital=hospital,
        email=pharmacist.email,
    )

    receive_response = client.post(
        f"/api/v1/prescriptions/{order_id}/receive",
        headers=auth_headers(pharmacist_token),
    )

    assert receive_response.status_code == 200
    assert receive_response.json()["status"] == "RECEIVED"

    start_response = client.post(
        f"/api/v1/prescriptions/{order_id}/start",
        headers=auth_headers(pharmacist_token),
    )

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "IN_PROGRESS"
    assert start_response.json()["started_at"] is not None




def test_dispensing_one_of_multiple_medications_keeps_episode_open(
    client,
    db: Session,
):
    """
    Dispensing one medication while another remains outstanding keeps
    an AWAITING_PHARMACY Episode open. The final medication closes it.
    """
    from app.core.context import RequestContext
    from app.modules.clinical_orders.enums import ClinicalOrderStatus
    from app.modules.clinical_orders.models import ClinicalOrder
    from app.modules.episode.models import (
        EpisodeFlowStatus,
        EpisodeStatus,
    )

    hospital = create_hospital(db)

    doctor = create_user(
        db,
        hospital=hospital,
        email=f"multi-med-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    pharmacist = create_user(
        db,
        hospital=hospital,
        email=f"multi-med-pharmacist-{uuid4()}@example.com",
        role_name="Pharmacist",
    )

    pharmacist_staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=__import__(
            "app.modules.organization.repository",
            fromlist=["HospitalRepository"],
        ).HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    pharmacist_staff = pharmacist_staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STAFF-MULTI-{uuid4().hex[:8]}",
            first_name="Multiple",
            last_name="Pharmacist",
            gender=Gender.FEMALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.PHARMACIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        ),
    )

    pharmacist_staff_service.link_user_account(
        pharmacist_staff.id,
        pharmacist.id,
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor,
    )

    doctor_token = authenticate(
        db,
        hospital=hospital,
        email=doctor.email,
    )

    def create_prescription(medicine_name, quantity):
        response = client.post(
            "/api/v1/prescriptions",
            headers=auth_headers(doctor_token),
            json={
                "encounter_id": str(encounter.id),
                "priority": "ROUTINE",
                "medicine_name": medicine_name,
                "strength": "500 mg",
                "dose": "500",
                "dose_unit": "mg",
                "route": "ORAL",
                "frequency": "QID",
                "duration": "3",
                "duration_unit": "days",
                "quantity": quantity,
                "directions": "Take after food.",
                "indication": "Fever.",
            },
        )

        assert response.status_code == 201
        return response.json()["clinical_order_id"]

    order_one_id = create_prescription(
        "Paracetamol",
        "12 tablets",
    )
    order_two_id = create_prescription(
        "Amoxicillin",
        "15 capsules",
    )

    episode = encounter.episode
    episode.flow_status = EpisodeFlowStatus.AWAITING_PHARMACY
    episode.status = EpisodeStatus.OPEN
    db.commit()
    db.refresh(episode)

    pharmacist_token = authenticate(
        db,
        hospital=hospital,
        email=pharmacist.email,
    )

    for order_id in (order_one_id, order_two_id):
        receive_response = client.post(
            f"/api/v1/prescriptions/{order_id}/receive",
            headers=auth_headers(pharmacist_token),
        )

        assert receive_response.status_code == 200
        assert receive_response.json()["status"] == "RECEIVED"

        start_response = client.post(
            f"/api/v1/prescriptions/{order_id}/start",
            headers=auth_headers(pharmacist_token),
        )

        assert start_response.status_code == 200
        assert start_response.json()["status"] == "IN_PROGRESS"

    context = RequestContext(
        user_id=pharmacist.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = DispensingService(
        dispensing_repository=DispensingRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        prescription_repository=PrescriptionRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
        episode_repository=EpisodeRepository(db),
    )

    service.dispense(
        context=context,
        order_id=order_one_id,
        quantity_dispensed="12 tablets",
        notes="First medication dispensed.",
    )

    first_order = (
        db.query(ClinicalOrder)
        .filter(ClinicalOrder.id == order_one_id)
        .one()
    )

    db.refresh(episode)

    assert first_order.status == ClinicalOrderStatus.COMPLETED
    assert episode.status == EpisodeStatus.OPEN
    assert (
        episode.flow_status
        == EpisodeFlowStatus.AWAITING_PHARMACY
    )
    assert episode.closed_at is None

    service.dispense(
        context=context,
        order_id=order_two_id,
        quantity_dispensed="15 capsules",
        notes="Final medication dispensed.",
    )

    second_order = (
        db.query(ClinicalOrder)
        .filter(ClinicalOrder.id == order_two_id)
        .one()
    )

    db.refresh(episode)

    assert second_order.status == ClinicalOrderStatus.COMPLETED
    assert episode.status == EpisodeStatus.CLOSED
    assert episode.closed_at is not None

def test_dispensing_last_medication_closes_awaiting_pharmacy_episode(
    client,
    db: Session,
):
    """
    Dispensing the final outstanding medication closes an Episode
    that is awaiting pharmacy.
    """
    from app.core.context import RequestContext
    from app.modules.clinical_orders.enums import ClinicalOrderStatus
    from app.modules.clinical_orders.models import ClinicalOrder
    from app.modules.episode.models import (
        EpisodeFlowStatus,
        EpisodeStatus,
    )

    hospital = create_hospital(db)

    doctor = create_user(
        db,
        hospital=hospital,
        email=f"lifecycle-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    pharmacist = create_user(
        db,
        hospital=hospital,
        email=f"lifecycle-pharmacist-{uuid4()}@example.com",
        role_name="Pharmacist",
    )

    pharmacist_staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=__import__(
            "app.modules.organization.repository",
            fromlist=["HospitalRepository"],
        ).HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    pharmacist_staff = pharmacist_staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STAFF-LIFE-{uuid4().hex[:8]}",
            first_name="Lifecycle",
            last_name="Pharmacist",
            gender=Gender.FEMALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.PHARMACIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        ),
    )

    pharmacist_staff_service.link_user_account(
        pharmacist_staff.id,
        pharmacist.id,
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor,
    )

    doctor_token = authenticate(
        db,
        hospital=hospital,
        email=doctor.email,
    )

    create_response = client.post(
        "/api/v1/prescriptions",
        headers=auth_headers(doctor_token),
        json={
            "encounter_id": str(encounter.id),
            "priority": "ROUTINE",
            "medicine_name": "Paracetamol",
            "strength": "500 mg",
            "dose": "500",
            "dose_unit": "mg",
            "route": "ORAL",
            "frequency": "QID",
            "duration": "3",
            "duration_unit": "days",
            "quantity": "12 tablets",
            "directions": "Take after food.",
            "indication": "Fever.",
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["clinical_order_id"]

    episode = encounter.episode
    episode.flow_status = EpisodeFlowStatus.AWAITING_PHARMACY
    episode.status = EpisodeStatus.OPEN
    db.commit()
    db.refresh(episode)

    pharmacist_token = authenticate(
        db,
        hospital=hospital,
        email=pharmacist.email,
    )

    receive_response = client.post(
        f"/api/v1/prescriptions/{order_id}/receive",
        headers=auth_headers(pharmacist_token),
    )

    assert receive_response.status_code == 200
    assert receive_response.json()["status"] == "RECEIVED"

    start_response = client.post(
        f"/api/v1/prescriptions/{order_id}/start",
        headers=auth_headers(pharmacist_token),
    )

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "IN_PROGRESS"

    context = RequestContext(
        user_id=pharmacist.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = DispensingService(
        dispensing_repository=DispensingRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        prescription_repository=PrescriptionRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
        episode_repository=EpisodeRepository(db),
    )

    dispensing = service.dispense(
        context=context,
        order_id=order_id,
        quantity_dispensed="12 tablets",
        notes="Dispensed in full.",
    )

    assert dispensing.id is not None

    order = (
        db.query(ClinicalOrder)
        .filter(ClinicalOrder.id == order_id)
        .one()
    )

    db.refresh(episode)

    assert order.status == ClinicalOrderStatus.COMPLETED
    assert order.completed_at is not None

    assert episode.status == EpisodeStatus.CLOSED
    assert episode.closed_at is not None


def test_pharmacist_can_dispense_in_progress_prescription(
    client,
    db: Session,
):
    hospital = create_hospital(db)

    doctor = create_user(
        db,
        hospital=hospital,
        email=f"dispense-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    pharmacist = create_user(
        db,
        hospital=hospital,
        email=f"dispense-pharmacist-{uuid4()}@example.com",
        role_name="Pharmacist",
    )

    pharmacist_staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=__import__(
            "app.modules.organization.repository",
            fromlist=["HospitalRepository"],
        ).HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    pharmacist_staff = pharmacist_staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STAFF-DISP-{uuid4().hex[:8]}",
            first_name="Dispensing",
            last_name="Pharmacist",
            gender=Gender.FEMALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.PHARMACIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        ),
    )

    pharmacist_staff_service.link_user_account(
        pharmacist_staff.id,
        pharmacist.id,
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor,
    )

    doctor_token = authenticate(
        db,
        hospital=hospital,
        email=doctor.email,
    )

    create_response = client.post(
        "/api/v1/prescriptions",
        headers=auth_headers(doctor_token),
        json={
            "encounter_id": str(encounter.id),
            "priority": "ROUTINE",
            "medicine_name": "Paracetamol",
            "strength": "500 mg",
            "dose": "500",
            "dose_unit": "mg",
            "route": "ORAL",
            "frequency": "QID",
            "duration": "3",
            "duration_unit": "days",
            "quantity": "12 tablets",
            "directions": "Take after food.",
            "indication": "Fever.",
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["clinical_order_id"]

    pharmacist_token = authenticate(
        db,
        hospital=hospital,
        email=pharmacist.email,
    )

    receive_response = client.post(
        f"/api/v1/prescriptions/{order_id}/receive",
        headers=auth_headers(pharmacist_token),
    )

    assert receive_response.status_code == 200

    start_response = client.post(
        f"/api/v1/prescriptions/{order_id}/start",
        headers=auth_headers(pharmacist_token),
    )

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "IN_PROGRESS"

    context = __import__(
        "app.core.context",
        fromlist=["RequestContext"],
    ).RequestContext(
        user_id=pharmacist.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = DispensingService(
        dispensing_repository=DispensingRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        prescription_repository=PrescriptionRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
        episode_repository=EpisodeRepository(db),
    )

    dispensing = service.dispense(
        context=context,
        order_id=order_id,
        quantity_dispensed="12 tablets",
        notes="Dispensed in full.",
    )

    assert dispensing.id is not None
    assert dispensing.dispensed_by == pharmacist_staff.id
    assert dispensing.quantity_dispensed == "12 tablets"
    assert dispensing.notes == "Dispensed in full."

    db.refresh(
        db.query(
            __import__(
                "app.modules.clinical_orders.models",
                fromlist=["ClinicalOrder"],
            ).ClinicalOrder
        )
        .filter(
            __import__(
                "app.modules.clinical_orders.models",
                fromlist=["ClinicalOrder"],
            ).ClinicalOrder.id == order_id,
        )
        .one()
    )

    from app.modules.clinical_orders.models import ClinicalOrder

    order = db.query(ClinicalOrder).filter(
        ClinicalOrder.id == order_id,
    ).one()

    assert order.status.value == "COMPLETED"
    assert order.completed_at is not None

    event = db.query(ClinicalEvent).filter(
        ClinicalEvent.encounter_id == encounter.id,
        ClinicalEvent.event_type == EventType.MEDICATION_DISPENSED,
    ).one()

    assert event.performed_by == pharmacist_staff.id
    assert event.payload["clinical_order_id"] == str(order.id)
    assert event.payload["prescription_id"] == str(
        dispensing.prescription_id,
    )
    assert event.payload["quantity_dispensed"] == "12 tablets"
