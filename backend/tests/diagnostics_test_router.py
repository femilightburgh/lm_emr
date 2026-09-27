"""
==============================================================================
LIGHTBURGH EMR

Diagnostics Router Tests
==============================================================================
"""

from uuid import uuid4

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client(db, tmp_path):
    from app.modules.diagnostics.api.router import (
        get_diagnostic_service,
    )
    from app.modules.diagnostics.api.router import (
        router as diagnostics_router,
    )
    from app.storage import LocalStorage

    def override_get_db():
        yield db

    def override_diagnostic_service():
        from app.modules.clinical_orders.repositories import (
            ClinicalOrderRepository,
        )
        from app.modules.diagnostics.repositories import (
            DiagnosticRepository,
        )
        from app.modules.diagnostics.services import (
            DiagnosticService,
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

        return DiagnosticService(
            repository=DiagnosticRepository(db),
            clinical_order_repository=ClinicalOrderRepository(db),
            episode_repository=EpisodeRepository(db),
            staff_repository=StaffRepository(db),
            event_service=ClinicalEventService(
                repository=ClinicalEventRepository(db),
            ),
            storage=LocalStorage(
                str(tmp_path / "storage"),
            ),
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        get_diagnostic_service
    ] = override_diagnostic_service

    yield TestClient(app)

    app.dependency_overrides.clear()


def create_hospital(
    db,
):
    from app.modules.organization.enums import (
        HospitalOwnership,
        HospitalType,
    )
    from app.modules.organization.schemas import HospitalCreate
    from app.modules.organization.service import HospitalService

    code = f"DIAG-{uuid4().hex[:8].upper()}"

    return HospitalService(db).create_hospital(
        HospitalCreate(
            name=f"Diagnostics Hospital {code}",
            code=code,
            hospital_type=HospitalType.GENERAL,
            ownership=HospitalOwnership.PRIVATE,
            email=f"{code.lower()}@example.com",
            phone="08000000000",
            address="1 Diagnostics Street",
            city="Lagos",
            state="Lagos",
        )
    )


def create_user(
    db,
    *,
    hospital,
    email: str | None = None,
    role_name: str = "Laboratory Scientist",
):
    from app.modules.identity.repository import IdentityRepository
    from app.modules.identity.user_service import UserService

    service = UserService(
        repository=IdentityRepository(db),
    )

    user = service.create_user(
        hospital_code=hospital.code,
        email=email or f"diagnostics-{uuid4()}@example.com",
        password="password123",
        role_name=role_name,
    )

    IdentityRepository(db).save()

    return user


def create_lab_staff(
    db,
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
            staff_number=f"DIAG-{uuid4().hex[:8].upper()}",
            first_name="Diagnostic",
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
    db,
    *,
    hospital,
    email: str,
):
    from app.modules.identity.auth_service import AuthService
    from app.modules.identity.repository import IdentityRepository
    from app.modules.identity.token_service import TokenService

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


def create_diagnostic_investigation(
    db,
    hospital,
):
    from app.modules.diagnostics.repositories import (
        DiagnosticRepository,
    )

    repository = DiagnosticRepository(db)

    investigation = repository.get_investigation_by_code(
        hospital_id=hospital.id,
        code="ECG",
    )

    if investigation is None:
        raise AssertionError(
            "Default ECG diagnostic investigation was not "
            "bootstrapped for the test hospital.",
        )

    return investigation


def create_diagnostic_order(
    db,
    hospital,
    doctor_user,
    investigation,
):
    from app.core.context import RequestContext
    from app.modules.clinical_orders.enums import ClinicalOrderType
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        PrescriptionRepository,
    )
    from app.modules.diagnostics.repositories import DiagnosticRepository
    from app.modules.laboratory.repositories.laboratory_test_repository import (
        LaboratoryTestRepository,
    )
    from app.modules.clinical_orders.services import ClinicalOrderService
    from app.modules.encounter.repositories.encounter_repository import (
        EncounterRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services.event_service import ClinicalEventService
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.staff.repository import StaffRepository

    _, encounter = __import__(
        "tests.clinical_orders.test_router",
        fromlist=["create_doctor_encounter"],
    ).create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

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
    )

    return service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.DIAGNOSTIC,
        priority="ROUTINE",
        details={
            "investigation_id": str(investigation.id),
        },
        items=[
            {
                "diagnostic_investigation_id": investigation.id,
            }
        ],
    )


def test_diagnostic_report_full_lifecycle(
    client,
    db,
):
    from app.core.context import RequestContext
    from app.modules.clinical_orders.enums import ClinicalOrderStatus
    from app.modules.clinical_orders.enums import ClinicalOrderType
    from app.modules.clinical_orders.repositories import (
        ClinicalOrderRepository,
        PrescriptionRepository,
    )
    from app.modules.clinical_orders.services import ClinicalOrderService
    from app.modules.diagnostics.enums import DiagnosticCategory
    from app.modules.diagnostics.repositories import DiagnosticRepository
    from app.modules.encounter.repositories.encounter_repository import (
        EncounterRepository,
    )
    from app.modules.events.repositories import ClinicalEventRepository
    from app.modules.events.services.event_service import ClinicalEventService
    from app.modules.episode.repositories.episode_repository import (
        EpisodeRepository,
    )
    from app.modules.staff.repository import StaffRepository

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"diagnostic-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    diagnostic_user = create_user(
        db,
        hospital=hospital,
        email=f"diagnostic-scientist-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=diagnostic_user,
    )

    investigation = create_diagnostic_investigation(
        db,
        hospital,
    )

    order = create_diagnostic_order(
        db,
        hospital,
        doctor_user,
        investigation,
    )

    diagnostic_token = authenticate(
        db,
        hospital=hospital,
        email=diagnostic_user.email,
    )

    receive_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(diagnostic_token),
    )

    assert receive_response.status_code == status.HTTP_200_OK

    start_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(diagnostic_token),
    )

    assert start_response.status_code == status.HTTP_200_OK

    report_response = client.post(
        "/api/v1/diagnostics/reports",
        headers=auth_headers(diagnostic_token),
        json={
            "order_id": str(order.id),
            "investigation_id": str(investigation.id),
            "category": DiagnosticCategory.CARDIOLOGY.value,
            "findings": "Sinus rhythm.",
            "impression": "Normal ECG.",
            "interpretation": "No acute abnormality identified.",
            "recommendations": "Clinical correlation where indicated.",
            "measurements": {
                "heart_rate": 72,
                "rhythm": "Sinus rhythm",
            },
        },
    )

    assert report_response.status_code == status.HTTP_201_CREATED

    report_body = report_response.json()

    report_id = report_body["id"]

    assert report_body["status"] == "DRAFT"
    assert report_body["findings"] == "Sinus rhythm."
    assert report_body["impression"] == "Normal ECG."
    assert report_body["reported_at"] is None
    assert report_body["recorded_by"] is None
    assert report_body["recorded_at"] is None

    update_response = client.put(
        f"/api/v1/diagnostics/reports/{report_id}",
        headers=auth_headers(diagnostic_token),
        json={
            "findings": "Sinus rhythm at 72 bpm.",
            "impression": "Normal ECG.",
            "interpretation": "No acute abnormality identified.",
            "recommendations": "Clinical correlation where indicated.",
            "measurements": {
                "heart_rate": 72,
                "rhythm": "Sinus rhythm",
            },
        },
    )

    assert update_response.status_code == status.HTTP_200_OK

    updated_body = update_response.json()

    assert updated_body["status"] == "DRAFT"
    assert updated_body["findings"] == "Sinus rhythm at 72 bpm."

    finalize_response = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/finalize",
        headers=auth_headers(diagnostic_token),
    )

    assert finalize_response.status_code == status.HTTP_200_OK

    finalized_body = finalize_response.json()

    assert finalized_body["status"] == "FINAL"
    assert finalized_body["reported_at"] is not None
    assert finalized_body["recorded_at"] is not None

    diagnostic_staff = StaffRepository(
        db,
    ).get_by_user_account_id(
        hospital.id,
        diagnostic_user.id,
    )

    assert diagnostic_staff is not None
    assert finalized_body["recorded_by"] == str(
        diagnostic_staff.id,
    )

    report_get = client.get(
        f"/api/v1/diagnostics/reports/{report_id}",
        headers=auth_headers(diagnostic_token),
    )

    assert report_get.status_code == status.HTTP_200_OK
    assert report_get.json()["status"] == "FINAL"

    update_after_finalize = client.put(
        f"/api/v1/diagnostics/reports/{report_id}",
        headers=auth_headers(diagnostic_token),
        json={
            "findings": "This must not overwrite the final report.",
            "impression": "Invalid update.",
            "interpretation": None,
            "recommendations": None,
            "measurements": None,
        },
    )

    assert (
        update_after_finalize.status_code
        == status.HTTP_409_CONFLICT
    )

    second_finalize = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/finalize",
        headers=auth_headers(diagnostic_token),
    )

    assert (
        second_finalize.status_code
        == status.HTTP_409_CONFLICT
    )


def test_diagnostic_report_attachment_lifecycle(
    client,
    db,
    tmp_path,
):
    from pathlib import Path

    from app.modules.clinical_orders.enums import ClinicalOrderType
    from app.modules.diagnostics.enums import DiagnosticCategory

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"attachment-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    diagnostic_user = create_user(
        db,
        hospital=hospital,
        email=f"attachment-scientist-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=diagnostic_user,
    )

    investigation = create_diagnostic_investigation(
        db,
        hospital,
    )

    order = create_diagnostic_order(
        db,
        hospital,
        doctor_user,
        investigation,
    )

    diagnostic_token = authenticate(
        db,
        hospital=hospital,
        email=diagnostic_user.email,
    )

    receive_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(diagnostic_token),
    )

    assert receive_response.status_code == 200

    start_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(diagnostic_token),
    )

    assert start_response.status_code == 200

    report_response = client.post(
        "/api/v1/diagnostics/reports",
        headers=auth_headers(diagnostic_token),
        json={
            "order_id": str(order.id),
            "investigation_id": str(investigation.id),
            "category": DiagnosticCategory.CARDIOLOGY.value,
            "findings": "Sinus rhythm.",
            "impression": "Normal ECG.",
            "interpretation": "No acute abnormality.",
            "recommendations": None,
            "measurements": {
                "heart_rate": 72,
                "rhythm": "Sinus rhythm",
            },
        },
    )

    assert report_response.status_code == 201

    report_id = report_response.json()["id"]

    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"\x00\x00\x00\nIDAT"
        b"\x08\xd7c\xf8\xcf\xc0\x00\x00"
        b"\x03\x01\x01\x00\x18\xdd\x8d\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    upload_response = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/attachments",
        headers=auth_headers(diagnostic_token),
        files={
            "file": (
                "ecg.png",
                png_bytes,
                "image/png",
            ),
        },
        data={
            "description": "ECG tracing image",
        },
    )

    assert upload_response.status_code == 201

    attachment_body = upload_response.json()

    attachment_id = attachment_body["id"]

    assert attachment_body["report_id"] == report_id
    assert attachment_body["file_name"] == "ecg.png"
    assert attachment_body["content_type"] == "image/png"
    assert attachment_body["description"] == "ECG tracing image"

    storage_key = attachment_body.get("storage_key")

    assert storage_key is None

    list_response = client.get(
        f"/api/v1/diagnostics/reports/{report_id}/attachments",
        headers=auth_headers(diagnostic_token),
    )

    assert list_response.status_code == 200

    attachments = list_response.json()

    assert len(attachments) == 1
    assert attachments[0]["id"] == attachment_id
    assert attachments[0]["file_name"] == "ecg.png"

    download_response = client.get(
        f"/api/v1/diagnostics/attachments/{attachment_id}",
        headers=auth_headers(diagnostic_token),
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "image/png"
    assert download_response.content == png_bytes

    storage_root = tmp_path / "storage" / "diagnostics"
    stored_files = list(
        storage_root.glob("*"),
    )

    assert len(stored_files) == 1
    assert stored_files[0].read_bytes() == png_bytes

    finalize_response = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/finalize",
        headers=auth_headers(diagnostic_token),
    )

    assert finalize_response.status_code == 200
    assert finalize_response.json()["status"] == "FINAL"

    second_upload = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/attachments",
        headers=auth_headers(diagnostic_token),
        files={
            "file": (
                "another.png",
                png_bytes,
                "image/png",
            ),
        },
    )

    assert second_upload.status_code == 409


def test_diagnostic_attachment_rejects_unsupported_file_type(
    client,
    db,
):
    from app.modules.diagnostics.enums import DiagnosticCategory

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"mime-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    diagnostic_user = create_user(
        db,
        hospital=hospital,
        email=f"mime-diagnostic-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=diagnostic_user,
    )

    investigation = create_diagnostic_investigation(
        db,
        hospital,
    )

    order = create_diagnostic_order(
        db,
        hospital,
        doctor_user,
        investigation,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=diagnostic_user.email,
    )

    assert client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(token),
    ).status_code == 200

    assert client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(token),
    ).status_code == 200

    report = client.post(
        "/api/v1/diagnostics/reports",
        headers=auth_headers(token),
        json={
            "order_id": str(order.id),
            "investigation_id": str(investigation.id),
            "category": DiagnosticCategory.CARDIOLOGY.value,
            "findings": "Test",
            "impression": "Test",
            "interpretation": "Test",
            "recommendations": None,
            "measurements": None,
        },
    )

    assert report.status_code == 201

    response = client.post(
        f"/api/v1/diagnostics/reports/{report.json()['id']}/attachments",
        headers=auth_headers(token),
        files={
            "file": (
                "malware.exe",
                b"not an executable",
                "application/octet-stream",
            ),
        },
    )

    assert response.status_code == 415


def test_diagnostic_attachment_rejects_oversized_file(
    client,
    db,
):
    from app.core.config import settings
    from app.modules.diagnostics.enums import DiagnosticCategory

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"size-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    diagnostic_user = create_user(
        db,
        hospital=hospital,
        email=f"size-diagnostic-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=diagnostic_user,
    )

    investigation = create_diagnostic_investigation(
        db,
        hospital,
    )

    order = create_diagnostic_order(
        db,
        hospital,
        doctor_user,
        investigation,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=diagnostic_user.email,
    )

    assert client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(token),
    ).status_code == 200

    assert client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(token),
    ).status_code == 200

    report = client.post(
        "/api/v1/diagnostics/reports",
        headers=auth_headers(token),
        json={
            "order_id": str(order.id),
            "investigation_id": str(investigation.id),
            "category": DiagnosticCategory.CARDIOLOGY.value,
            "findings": "Test",
            "impression": "Test",
            "interpretation": "Test",
            "recommendations": None,
            "measurements": None,
        },
    )

    assert report.status_code == 201

    oversized_content = b"x" * (
        settings.storage_max_file_size_mb * 1024 * 1024 + 1
    )

    response = client.post(
        f"/api/v1/diagnostics/reports/{report.json()['id']}/attachments",
        headers=auth_headers(token),
        files={
            "file": (
                "oversized.png",
                oversized_content,
                "image/png",
            ),
        },
    )

    assert response.status_code == 413


def test_diagnostic_attachment_cannot_be_accessed_from_another_hospital(
    client,
    db,
    hospital,
    hospital_two,
):
    from app.bootstrap.diagnostics import (
        bootstrap_diagnostic_investigations,
    )
    from app.modules.diagnostics.enums import DiagnosticCategory
    from app.modules.identity.role_seeder import seed_default_roles

    seed_default_roles(
        db,
        hospital.id,
    )
    seed_default_roles(
        db,
        hospital_two.id,
    )

    bootstrap_diagnostic_investigations(
        session=db,
        hospital_id=hospital.id,
    )
    bootstrap_diagnostic_investigations(
        session=db,
        hospital_id=hospital_two.id,
    )

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"cross-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    diagnostic_user = create_user(
        db,
        hospital=hospital,
        email=f"cross-diagnostic-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=diagnostic_user,
    )

    investigation = create_diagnostic_investigation(
        db,
        hospital,
    )

    order = create_diagnostic_order(
        db,
        hospital,
        doctor_user,
        investigation,
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=diagnostic_user.email,
    )

    assert client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(token),
    ).status_code == 200

    assert client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(token),
    ).status_code == 200

    report = client.post(
        "/api/v1/diagnostics/reports",
        headers=auth_headers(token),
        json={
            "order_id": str(order.id),
            "investigation_id": str(investigation.id),
            "category": DiagnosticCategory.CARDIOLOGY.value,
            "findings": "Cross hospital test",
            "impression": "Test",
            "interpretation": "Test",
            "recommendations": None,
            "measurements": None,
        },
    )

    assert report.status_code == 201
    report_id = report.json()["id"]

    upload = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/attachments",
        headers=auth_headers(token),
        files={
            "file": (
                "ecg.png",
                b"test image",
                "image/png",
            ),
        },
    )

    assert upload.status_code == 201

    attachment_id = upload.json()["id"]

    other_user = create_user(
        db,
        hospital=hospital_two,
        email=f"cross-other-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital_two,
        user=other_user,
    )

    other_token = authenticate(
        db,
        hospital=hospital_two,
        email=other_user.email,
    )

    response = client.get(
        f"/api/v1/diagnostics/attachments/{attachment_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 404


def test_new_hospital_receives_default_diagnostic_catalogue(
    db,
):
    from app.modules.diagnostics.repositories import (
        DiagnosticRepository,
    )

    hospital = create_hospital(db)

    repository = DiagnosticRepository(db)

    investigations = (
        repository.list_active_investigations(
            hospital_id=hospital.id,
        )
    )

    expected_codes = {
        "XRAY",
        "ULTRASOUND",
        "CT",
        "MRI",
        "ECG",
        "ECHO",
        "EEG",
        "PFT",
        "AUDIOMETRY",
        "ENDOSCOPY",
    }

    actual_codes = {
        investigation.code
        for investigation in investigations
    }

    assert len(investigations) == 10
    assert actual_codes == expected_codes


def test_diagnostic_report_can_be_retrieved_by_order(
    client,
    db,
):
    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        email=f"by-order-doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    diagnostic_user = create_user(
        db,
        hospital=hospital,
        email=f"by-order-diagnostic-{uuid4()}@example.com",
        role_name="Laboratory Scientist",
    )

    create_lab_staff(
        db,
        hospital=hospital,
        user=diagnostic_user,
    )

    investigation = create_diagnostic_investigation(
        db,
        hospital,
    )

    order = create_diagnostic_order(
        db,
        hospital,
        doctor_user,
        investigation,
    )

    diagnostic_token = authenticate(
        db,
        hospital=hospital,
        email=diagnostic_user.email,
    )

    receive_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/receive",
        headers=auth_headers(diagnostic_token),
    )

    assert receive_response.status_code == 200

    start_response = client.post(
        f"/api/v1/clinical-orders/{order.id}/start",
        headers=auth_headers(diagnostic_token),
    )

    assert start_response.status_code == 200

    create_response = client.post(
        "/api/v1/diagnostics/reports",
        headers=auth_headers(diagnostic_token),
        json={
            "order_id": str(order.id),
            "investigation_id": str(investigation.id),
            "category": investigation.category.value,
            "findings": "Normal sinus rhythm.",
            "impression": "Normal ECG.",
            "interpretation": "No acute abnormality.",
            "recommendations": None,
            "measurements": {
                "heart_rate": 72,
            },
        },
    )

    assert create_response.status_code == 201

    report_id = create_response.json()["id"]

    finalize_response = client.post(
        f"/api/v1/diagnostics/reports/{report_id}/finalize",
        headers=auth_headers(diagnostic_token),
    )

    assert finalize_response.status_code == 200

    doctor_token = authenticate(
        db,
        hospital=hospital,
        email=doctor_user.email,
    )

    response = client.get(
        f"/api/v1/diagnostics/reports/by-order/{order.id}",
        headers=auth_headers(doctor_token),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == report_id
    assert body["order_id"] == str(order.id)
    assert body["status"] == "FINAL"
    assert body["findings"] == "Normal sinus rhythm."
    assert body["impression"] == "Normal ECG."
