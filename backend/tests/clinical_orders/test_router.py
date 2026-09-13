"""
==============================================================================
LIGHTBURGH EMR

Clinical Order API Tests
==============================================================================
"""

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app

from app.modules.clinical_orders.enums import ClinicalOrderType
from app.modules.events.models import ClinicalEvent
from app.modules.events.enums import EventType

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.repositories.episode_disposition_repository import (
    EpisodeDispositionRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import (
    EpisodeService,
)

from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.identity.auth_service import AuthService
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.role_permission_repository import (
    RolePermissionRepository,
)
from app.modules.identity.role_permission_service import (
    RolePermissionService,
)
from app.modules.identity.token_service import TokenService
from app.modules.identity.user_service import UserService

from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.models import Hospital
from app.modules.laboratory.models.laboratory_test import LaboratoryTest
from app.modules.organization.schemas import HospitalCreate
from app.modules.organization.service import HospitalService

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


# ============================================================================
# Test Client
# ============================================================================


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


# ============================================================================
# Helpers
# ============================================================================


def create_hospital(
    db: Session,
) -> Hospital:
    code = f"ORDERS-{uuid4().hex[:8].upper()}"

    service = HospitalService(db)

    return service.create_hospital(
        HospitalCreate(
            name=f"Clinical Orders Hospital {code}",
            code=code,
            hospital_type=HospitalType.GENERAL,
            ownership=HospitalOwnership.PRIVATE,
            email=f"{code.lower()}@example.com",
            phone="08000000000",
            address="1 Order Street",
            city="Lagos",
            state="Lagos",
        )
    )


def create_user(
    db: Session,
    *,
    hospital: Hospital,
    email: str,
    role_name: str,
    password: str = "password123",
):
    repository = IdentityRepository(db)

    service = UserService(
        repository=repository,
    )

    user = service.create_user(
        hospital_code=hospital.code,
        email=email,
        password=password,
        role_name=role_name,
    )

    repository.save()
    repository.refresh(user)

    return user


def authenticate(
    db: Session,
    *,
    hospital: Hospital,
    email: str,
    password: str = "password123",
) -> str:
    repository = IdentityRepository(db)

    service = AuthService(
        repository=repository,
        token_service=TokenService(),
    )

    response = service.login(
        hospital_code=hospital.code,
        email=email,
        password=password,
    )

    return response.access_token


def auth_headers(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def create_doctor_encounter(
    db: Session,
    hospital: Hospital,
    user,
):
    from app.core.context import RequestContext

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
            hospital_number=f"API-ORD-{uuid4().hex[:8]}",
            first_name="Doctor",
            last_name="Patient",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )

    staff = StaffService(
        repository=StaffRepository(db),
        hospital_repository=__import__(
            "app.modules.organization.repository",
            fromlist=["HospitalRepository"],
        ).HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    ).create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STAFF-ORD-{uuid4().hex[:8]}",
            first_name="Doctor",
            last_name="Tester",
            gender=Gender.MALE,
            date_of_birth=date(1985, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
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
        encounter_service=EncounterService(
            repository=EncounterRepository(db),
            episode_repository=episode_repository,
            staff_repository=StaffRepository(
                session=db,
            ),
        ),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
        disposition_repository=EpisodeDispositionRepository(db),
    ).create_episode(
        context=context,
        patient_id=patient.id,
        title="Doctor Order Test Episode",
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

    return staff, encounter


def assign_permission(
    db: Session,
    *,
    hospital: Hospital,
    role_name: str,
    permission_code: str,
):
    from app.modules.identity.models import Role

    role = (
        db.query(Role)
        .filter(
            Role.hospital_id == hospital.id,
            Role.name == role_name,
        )
        .one()
    )

    RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=__import__(
            "app.modules.identity.permission_repository",
            fromlist=["PermissionRepository"],
        ).PermissionRepository(db),
    ).assign_permission(
        role_id=role.id,
        permission_code=permission_code,
    )

    db.commit()


# ============================================================================
# Create
# ============================================================================


def test_create_clinical_order_endpoint(
    client,
    db,
):
    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email=f"doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    staff, encounter = create_doctor_encounter(
        db,
        hospital,
        user,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    response = client.post(
        "/api/v1/clinical-orders",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "order_type": "LABORATORY",
            "priority": "ROUTINE",
            "details": {
                "test_code": "CBC",
                "test_name": "Full Blood Count",
            },
            "items": [
                {
                    "laboratory_test_id": str(laboratory_test.id),
                }
            ],
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["encounter_id"] == str(encounter.id)
    assert body["ordered_by"] == str(staff.id)
    assert body["order_type"] == "LABORATORY"
    assert body["status"] == "REQUESTED"
    assert len(body["items"]) == 1
    assert body["items"][0]["laboratory_test_id"] == str(laboratory_test.id)
    assert body["items"][0]["diagnostic_investigation_id"] is None

    event = db.query(ClinicalEvent).filter(
        ClinicalEvent.encounter_id == encounter.id,
        ClinicalEvent.event_type == EventType.INVESTIGATION_ORDERED,
    ).one()

    assert event.payload["clinical_order_id"] == body["id"]


# ============================================================================
# Authorization
# ============================================================================


def test_user_without_create_permission_cannot_create_clinical_order(
    client,
    db,
):
    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email=f"custom-{uuid4()}@example.com",
        role_name="Accountant",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        user,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.post(
        "/api/v1/clinical-orders",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "order_type": "LABORATORY",
            "priority": "ROUTINE",
            "details": {
                "test_code": "CBC",
            },
        },
    )

    assert response.status_code == 403


def test_doctor_can_read_clinical_order(
    client,
    db,
):
    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email=f"doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        user,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    create_response = client.post(
        "/api/v1/clinical-orders",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "order_type": "MEDICATION",
            "priority": "URGENT",
            "details": {
                "medication_id": str(uuid4()),
                "dose": "500 mg",
            },
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/clinical-orders/{order_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_doctor_can_cancel_clinical_order(
    client,
    db,
):
    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email=f"doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        user,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    create_response = client.post(
        "/api/v1/clinical-orders",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "order_type": "RADIOLOGY",
            "priority": "ROUTINE",
            "details": {
                "study_code": "CXR",
            },
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/clinical-orders/{order_id}/cancel",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_doctor_can_create_diagnostic_order_and_diagnostics_queue_returns_it(
    client,
    db,
):
    from app.core.context import RequestContext
    from app.modules.clinical_orders.enums import ClinicalOrderType
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        PrescriptionRepository,
    )
    from app.modules.clinical_orders.services import (
        ClinicalOrderService,
    )
    from app.modules.diagnostics.repositories import (
        DiagnosticRepository,
    )
    from app.modules.laboratory.repositories import (
        LaboratoryTestRepository,
    )
    from app.modules.encounter.repositories.encounter_repository import (
        EncounterRepository,
    )
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.events.repositories import (
        ClinicalEventRepository,
    )
    from app.modules.events.services.event_service import (
        ClinicalEventService,
    )
    from app.modules.staff.repository import StaffRepository

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"diagnostic-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    diagnostic_repository = DiagnosticRepository(db)

    ecg = diagnostic_repository.get_investigation_by_code(
        hospital_id=hospital.id,
        code="ECG",
    )

    assert ecg is not None
    assert ecg.code == "ECG"
    assert ecg.name == "Electrocardiogram"
    assert ecg.category.value == "CARDIOLOGY"

    doctor_context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    order_service = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        laboratory_test_repository=LaboratoryTestRepository(db),
        diagnostic_repository=diagnostic_repository,
    )

    order = order_service.create_order(
        context=doctor_context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.DIAGNOSTIC,
        priority="ROUTINE",
        details={
            "investigation_id": str(ecg.id),
        },
        items=[
            {
                "diagnostic_investigation_id": ecg.id,
            }
        ],
    )

    assert order.order_type == ClinicalOrderType.DIAGNOSTIC
    assert order.status.value == "REQUESTED"
    assert order.details["investigation_id"] == str(ecg.id)

    assert len(order.items) == 1
    assert order.items[0].diagnostic_investigation_id == ecg.id
    assert order.items[0].laboratory_test_id is None
    assert order.items[0].details["investigation_code"] == "ECG"
    assert order.items[0].details["investigation_name"] == "Electrocardiogram"
    assert order.items[0].details["diagnostic_category"] == "CARDIOLOGY"

    token = authenticate(
        db,
        hospital=hospital,
        email=doctor_user.email,
    )

    response = client.get(
        "/api/v1/clinical-orders/queue/diagnostics",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    queue_item = next(
        item
        for item in body
        if item["id"] == str(order.id)
    )

    assert queue_item["order_type"] == "DIAGNOSTIC"
    assert queue_item["status"] == "REQUESTED"
    assert len(queue_item["items"]) == 1
    assert queue_item["items"][0]["diagnostic_investigation_id"] == str(ecg.id)
    assert queue_item["items"][0]["laboratory_test_id"] is None
    assert queue_item["items"][0]["details"]["investigation_code"] == "ECG"
    assert queue_item["items"][0]["details"]["investigation_name"] == (
        "Electrocardiogram"
    )
    assert queue_item["items"][0]["details"]["diagnostic_category"] == (
        "CARDIOLOGY"
    )

def test_doctor_can_receive_single_grouped_laboratory_item(
    client,
    db,
):
    from app.core.context import RequestContext
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        MedicationTreatmentRepository,
        PrescriptionRepository,
    )
    from app.modules.clinical_orders.services import (
        ClinicalOrderService,
        InpatientMedicationService,
    )
    from app.modules.diagnostics.repositories.diagnostic_repository import (
        DiagnosticRepository,
    )
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services import ClinicalEventService
    from app.modules.laboratory.repositories.laboratory_test_repository import (
        LaboratoryTestRepository,
    )

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"grouped-receive-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    laboratory_tests = db.query(LaboratoryTest).filter(
        LaboratoryTest.hospital_id == hospital.id,
        LaboratoryTest.code.in_(["APTT", "BCS", "CBC"]),
        LaboratoryTest.active.is_(True),
    ).order_by(LaboratoryTest.code).all()

    assert [test.code for test in laboratory_tests] == [
        "APTT",
        "BCS",
        "CBC",
    ]

    context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        laboratory_test_repository=LaboratoryTestRepository(db),
        diagnostic_repository=DiagnosticRepository(db),
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
        items=[
            {"laboratory_test_id": test.id}
            for test in laboratory_tests
        ],
    )

    target_item = next(
        item
        for item in order.items
        if item.details["test_code"] == "CBC"
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=doctor_user.email,
    )

    response = client.post(
        f"/api/v1/clinical-orders/items/{target_item.id}/receive",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    returned_target = next(
        item
        for item in body["items"]
        if item["id"] == str(target_item.id)
    )

    assert returned_target["status"] == "RECEIVED"

    sibling_statuses = {
        item["details"]["test_code"]: item["status"]
        for item in body["items"]
        if item["id"] != str(target_item.id)
    }

    assert sibling_statuses == {
        "APTT": "REQUESTED",
        "BCS": "REQUESTED",
    }


def test_doctor_can_start_single_received_grouped_laboratory_item(
    client,
    db,
):
    from app.core.context import RequestContext
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        MedicationTreatmentRepository,
        PrescriptionRepository,
    )
    from app.modules.clinical_orders.services import (
        ClinicalOrderService,
        InpatientMedicationService,
    )
    from app.modules.diagnostics.repositories.diagnostic_repository import (
        DiagnosticRepository,
    )
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services import ClinicalEventService
    from app.modules.laboratory.repositories.laboratory_test_repository import (
        LaboratoryTestRepository,
    )

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"grouped-start-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    laboratory_tests = db.query(LaboratoryTest).filter(
        LaboratoryTest.hospital_id == hospital.id,
        LaboratoryTest.code.in_(["APTT", "BCS", "CBC"]),
        LaboratoryTest.active.is_(True),
    ).order_by(LaboratoryTest.code).all()

    context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        laboratory_test_repository=LaboratoryTestRepository(db),
        diagnostic_repository=DiagnosticRepository(db),
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
        items=[
            {"laboratory_test_id": test.id}
            for test in laboratory_tests
        ],
    )

    target_item = next(
        item
        for item in order.items
        if item.details["test_code"] == "CBC"
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=doctor_user.email,
    )

    receive_response = client.post(
        f"/api/v1/clinical-orders/items/{target_item.id}/receive",
        headers=auth_headers(token),
    )

    assert receive_response.status_code == 200

    start_response = client.post(
        f"/api/v1/clinical-orders/items/{target_item.id}/start",
        headers=auth_headers(token),
    )

    assert start_response.status_code == 200

    body = start_response.json()

    returned_target = next(
        item
        for item in body["items"]
        if item["id"] == str(target_item.id)
    )

    assert returned_target["status"] == "IN_PROGRESS"

    sibling_statuses = {
        item["details"]["test_code"]: item["status"]
        for item in body["items"]
        if item["id"] != str(target_item.id)
    }

    assert sibling_statuses == {
        "APTT": "REQUESTED",
        "BCS": "REQUESTED",
    }


def test_grouped_laboratory_item_cannot_be_accessed_across_hospitals(
    client,
    db,
):
    from app.core.context import RequestContext
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        MedicationTreatmentRepository,
        PrescriptionRepository,
    )
    from app.modules.clinical_orders.services import (
        ClinicalOrderService,
        InpatientMedicationService,
    )
    from app.modules.diagnostics.repositories.diagnostic_repository import (
        DiagnosticRepository,
    )
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services import ClinicalEventService
    from app.modules.laboratory.repositories.laboratory_test_repository import (
        LaboratoryTestRepository,
    )

    hospital_a = create_hospital(db)
    hospital_b = create_hospital(db)

    doctor_a = create_user(
        db,
        hospital=hospital_a,
        email=f"tenant-a-{uuid4()}@example.com",
        role_name="Doctor",
    )

    doctor_b = create_user(
        db,
        hospital=hospital_b,
        email=f"tenant-b-{uuid4()}@example.com",
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital_a,
        doctor_a,
    )

    laboratory_test = db.query(LaboratoryTest).filter(
        LaboratoryTest.hospital_id == hospital_a.id,
        LaboratoryTest.code == "CBC",
        LaboratoryTest.active.is_(True),
    ).one()

    context = RequestContext(
        user_id=doctor_a.id,
        hospital_id=hospital_a.id,
        permissions=frozenset(),
    )

    service = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        laboratory_test_repository=LaboratoryTestRepository(db),
        diagnostic_repository=DiagnosticRepository(db),
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
        items=[
            {"laboratory_test_id": laboratory_test.id},
        ],
    )

    target_item = order.items[0]

    token_b = authenticate(
        db,
        hospital=hospital_b,
        email=doctor_b.email,
    )

    response = client.post(
        f"/api/v1/clinical-orders/items/{target_item.id}/receive",
        headers=auth_headers(token_b),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Clinical Order Item not found."

