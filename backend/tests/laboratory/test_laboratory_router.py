"""
==============================================================================
LIGHTBURGH EMR

Laboratory API Tests
==============================================================================
"""

from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.bootstrap.laboratory import (
    bootstrap_laboratory_tests,
)
from app.modules.identity.auth_service import AuthService
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.token_service import TokenService
from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.schemas import HospitalCreate
from app.modules.organization.service import HospitalService


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def create_hospital(
    db: Session,
):
    code = f"LAB-{uuid4().hex[:8].upper()}"

    return HospitalService(db).create_hospital(
        HospitalCreate(
            name=f"Laboratory Hospital {code}",
            code=code,
            hospital_type=HospitalType.GENERAL,
            ownership=HospitalOwnership.PRIVATE,
            email=f"{code.lower()}@example.com",
            phone="08000000000",
            address="1 Laboratory Street",
            city="Lagos",
            state="Lagos",
        )
    )


def create_user(
    db: Session,
    *,
    hospital,
    role_name: str = "Laboratory Scientist",
):
    service = __import__(
        "app.modules.identity.user_service",
        fromlist=["UserService"],
    ).UserService(
        repository=IdentityRepository(db),
    )

    user = service.create_user(
        hospital_code=hospital.code,
        email=f"lab-{uuid4()}@example.com",
        password="password123",
        role_name=role_name,
    )

    IdentityRepository(db).save()

    return user


def create_lab_staff(
    db: Session,
    *,
    hospital,
    user,
):
    from datetime import date

    from app.modules.organization.repository import (
        HospitalRepository,
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

    staff = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    ).create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"LAB-{uuid4().hex[:8].upper()}",
            first_name="Laboratory",
            last_name="Scientist",
            gender=Gender.FEMALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.LABORATORY_SCIENTIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff.user_account_id = user.id
    db.flush()

    return staff


def authenticate(
    db: Session,
    *,
    hospital,
    email: str,
):
    service = AuthService(
        repository=IdentityRepository(db),
        token_service=TokenService(),
    )

    return service.login(
        hospital_code=hospital.code,
        email=email,
        password="password123",
    ).access_token


def auth_headers(
    token: str,
):
    return {
        "Authorization": f"Bearer {token}",
    }


def test_list_laboratory_tests_returns_catalogue(
    client,
    db,
):
    hospital = create_hospital(db)

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    user = create_user(
        db,
        hospital=hospital,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/laboratory/tests",
        headers=auth_headers(token),
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert isinstance(body, list)

    codes = [
        item["code"]
        for item in body
    ]

    assert "CBC" in codes

    cbc = next(
        item
        for item in body
        if item["code"] == "CBC"
    )

    assert cbc["name"] == "Full Blood Count"
    assert cbc["specimen"] == "EDTA blood"
    assert cbc["active"] is True

    assert "analytes" in cbc

    analyte_codes = [
        analyte["code"]
        for analyte in cbc["analytes"]
    ]

    assert "hemoglobin" in analyte_codes
    assert "white_cell_count" in analyte_codes
    assert "platelets" in analyte_codes


def test_laboratory_test_catalogue_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/laboratory/tests",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_without_clinical_order_read_permission_cannot_list_laboratory_tests(
    client,
    db,
):
    hospital = create_hospital(db)

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    user = create_user(
        db,
        hospital=hospital,
        role_name="Accountant",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/laboratory/tests",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_laboratory_queue_returns_patient_and_order_context(
    client,
    db,
):
    from app.modules.clinical_orders.models import ClinicalOrder
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        PrescriptionRepository,
    )
    from app.modules.clinical_orders.services import (
        ClinicalOrderService,
    )
    from app.modules.clinical_orders.enums import (
        ClinicalOrderType,
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
        role_name="Doctor",
    )

    lab_user = create_user(
        db,
        hospital=hospital,
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=lab_user,
    )

    _, encounter = __import__(
        "tests.clinical_orders.test_router",
        fromlist=["create_doctor_encounter"],
    ).create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    from app.core.context import RequestContext

    doctor_context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    doctor_staff = (
        StaffRepository(db)
        .get_by_user_account_id(
            hospital_id=hospital.id,
            user_account_id=doctor_user.id,
        )
    )

    assert doctor_staff is not None

    order_service = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
    )

    order = order_service.create_order(
        context=doctor_context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
    )

    lab_token = authenticate(
        db,
        hospital=hospital,
        email=lab_user.email,
    )

    response = client.get(
        "/api/v1/clinical-orders/queue/laboratory",
        headers=auth_headers(lab_token),
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    queue_item = next(
        item
        for item in body
        if item["id"] == str(order.id)
    )

    assert queue_item["patient_name"] == (
        "Doctor Patient"
    )
    assert queue_item["hospital_number"].startswith(
        "API-ORD-"
    )
    assert queue_item["episode_number"]
    assert queue_item["ordering_clinician_name"] == (
        "Doctor Tester"
    )
    assert queue_item["order_type"] == "LABORATORY"
    assert queue_item["status"] == "REQUESTED"
    assert queue_item["priority"] == "ROUTINE"
    assert queue_item["details"]["test_code"] == "CBC"


def test_laboratory_scientist_can_start_and_record_result(
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

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    lab_user = create_user(
        db,
        hospital=hospital,
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=lab_user,
    )

    _, encounter = __import__(
        "tests.clinical_orders.test_router",
        fromlist=["create_doctor_encounter"],
    ).create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

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
    )

    order = order_service.create_order(
        context=doctor_context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
    )

    lab_token = authenticate(
        db,
        hospital=hospital,
        email=lab_user.email,
    )

    receive_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(lab_token),
    )

    assert receive_response.status_code == status.HTTP_200_OK
    assert receive_response.json()["status"] == "RECEIVED"

    start_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(lab_token),
    )

    assert start_response.status_code == status.HTTP_200_OK

    started_body = start_response.json()

    assert started_body["id"] == str(order.id)
    assert started_body["status"] == "IN_PROGRESS"
    assert started_body["started_at"] is not None

    result_response = client.post(
        "/api/v1/clinical-results",
        headers=auth_headers(lab_token),
        json={
            "order_id": str(order.id),
            "result_type": "LABORATORY",
            "result_data": {
                "hemoglobin": 13.2,
                "white_cell_count": 6.8,
                "platelets": 245,
                "interpretation": "Within expected limits.",
            },
        },
    )

    print("\n===== RESULT RESPONSE =====")
    print("STATUS:", result_response.status_code)
    print("BODY:", result_response.text)

    assert result_response.status_code == status.HTTP_201_CREATED

    result_body = result_response.json()

    assert result_body["order_id"] == str(order.id)
    assert result_body["result_type"] == "LABORATORY"
    assert result_body["result_data"]["hemoglobin"] == 13.2

    db.refresh(order)

    assert order.status.value == "COMPLETED"
    assert order.completed_at is not None


def test_laboratory_scientist_can_receive_lab_order(
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
        ClinicalEventService
    )
    from app.modules.staff.repository import StaffRepository

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    lab_user = create_user(
        db,
        hospital=hospital,
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=lab_user,
    )

    _, encounter = __import__(
        "tests.clinical_orders.test_router",
        fromlist=["create_doctor_encounter"],
    ).create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

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
    )

    order = order_service.create_order(
        context=doctor_context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
    )

    lab_token = authenticate(
        db,
        hospital=hospital,
        email=lab_user.email,
    )

    response = client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(lab_token),
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == str(order.id)
    assert body["status"] == "RECEIVED"

    db.refresh(order)

    assert order.status.value == "RECEIVED"



def test_laboratory_scientist_can_save_draft_and_finalize_result(
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
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.encounter.repositories.encounter_repository import (
        EncounterRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services.event_service import ClinicalEventService
    from app.modules.staff.repository import StaffRepository

    hospital = create_hospital(db)

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    lab_user = create_user(
        db,
        hospital=hospital,
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=lab_user,
    )

    _, encounter = __import__(
        "tests.clinical_orders.test_router",
        fromlist=["create_doctor_encounter"],
    ).create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    doctor_context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    order = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
    ).create_order(
        context=doctor_context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
    )

    lab_token = authenticate(
        db,
        hospital=hospital,
        email=lab_user.email,
    )

    receive_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(lab_token),
    )

    assert receive_response.status_code == status.HTTP_200_OK

    start_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(lab_token),
    )

    assert start_response.status_code == status.HTTP_200_OK

    result_response = client.post(
        "/api/v1/clinical-results",
        headers=auth_headers(lab_token),
        json={
            "order_id": str(order.id),
            "result_type": "LABORATORY",
            "status": "DRAFT",
            "specimen": "EDTA blood",
            "interpretation": "Mild anaemia.",
            "values": [],
        },
    )

    assert result_response.status_code == status.HTTP_201_CREATED

    draft_body = result_response.json()

    assert draft_body["order_id"] == str(order.id)
    assert draft_body["status"] == "DRAFT"
    assert draft_body["specimen"] == "EDTA blood"

    finalize_response = client.post(
        f"/api/v1/clinical-results/{draft_body['id']}/finalize",
        headers=auth_headers(lab_token),
    )

    assert finalize_response.status_code == status.HTTP_200_OK

    final_body = finalize_response.json()

    assert final_body["id"] == draft_body["id"]
    assert final_body["status"] == "FINAL"
    assert final_body["reported_at"] is not None

    db.refresh(order)

    assert order.status.value == "COMPLETED"
    assert order.completed_at is not None


def test_laboratory_scientist_cannot_finalize_result_twice(
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
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.encounter.repositories.encounter_repository import (
        EncounterRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services.event_service import ClinicalEventService
    from app.modules.staff.repository import StaffRepository

    hospital = create_hospital(db)

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    lab_user = create_user(
        db,
        hospital=hospital,
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=lab_user,
    )

    _, encounter = __import__(
        "tests.clinical_orders.test_router",
        fromlist=["create_doctor_encounter"],
    ).create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    doctor_context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    order = ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
    ).create_order(
        context=doctor_context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
    )

    lab_token = authenticate(
        db,
        hospital=hospital,
        email=lab_user.email,
    )

    client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(lab_token),
    )

    client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(lab_token),
    )

    result_response = client.post(
        "/api/v1/clinical-results",
        headers=auth_headers(lab_token),
        json={
            "order_id": str(order.id),
            "result_type": "LABORATORY",
            "status": "DRAFT",
            "values": [],
        },
    )

    assert result_response.status_code == status.HTTP_201_CREATED

    result_id = result_response.json()["id"]

    first_finalize = client.post(
        f"/api/v1/clinical-results/{result_id}/finalize",
        headers=auth_headers(lab_token),
    )

    assert first_finalize.status_code == status.HTTP_200_OK

    second_finalize = client.post(
        f"/api/v1/clinical-results/{result_id}/finalize",
        headers=auth_headers(lab_token),
    )

    assert second_finalize.status_code == status.HTTP_409_CONFLICT


def test_laboratory_catalogue_update_changes_reference_metadata(
    db,
):
    from app.modules.laboratory.models import LaboratoryTest
    from app.modules.laboratory.repositories import (
        LaboratoryTestRepository,
    )
    from app.modules.laboratory.services import (
        LaboratoryTestService,
    )

    hospital = create_hospital(db)

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    test = db.query(LaboratoryTest).filter(
        LaboratoryTest.hospital_id == hospital.id,
        LaboratoryTest.code == "CBC",
    ).one()

    analyte = test.analytes[0]

    service = LaboratoryTestService(
        repository=LaboratoryTestRepository(db),
    )

    updated = service.update_analyte(
        hospital_id=hospital.id,
        test_code="CBC",
        analyte_id=analyte.id,
        updates={
            "reference_low": 12,
            "reference_high": 16,
        },
    )

    assert updated.reference_low == 12
    assert updated.reference_high == 16


def test_laboratory_catalogue_update_rejects_invalid_range(
    db,
):
    from app.modules.laboratory.models import LaboratoryTest
    from app.modules.laboratory.repositories import (
        LaboratoryTestRepository,
    )
    from app.modules.laboratory.services import (
        LaboratoryTestService,
    )
    from app.modules.laboratory.exceptions import (
        LaboratoryReferenceRangeError,
    )

    hospital = create_hospital(db)

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )
    db.flush()

    test = db.query(LaboratoryTest).filter(
        LaboratoryTest.hospital_id == hospital.id,
        LaboratoryTest.code == "CBC",
    ).one()

    analyte = test.analytes[0]

    service = LaboratoryTestService(
        repository=LaboratoryTestRepository(db),
    )

    with pytest.raises(LaboratoryReferenceRangeError):
        service.update_analyte(
            hospital_id=hospital.id,
            test_code="CBC",
            analyte_id=analyte.id,
            updates={
                "reference_low": 16,
                "reference_high": 12,
            },
        )
