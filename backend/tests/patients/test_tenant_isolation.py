"""
==============================================================================
LIGHTBURGH EMR

Patient Tenant Isolation Tests
==============================================================================

Purpose
-------
Verifies hospital tenancy and hospital-scoped patient identification.

Tests prove that one hospital cannot:
- Retrieve another hospital's patient.
- Update another hospital's patient.
- Search for another hospital's patient.

Tests also prove that:
- The same hospital number may exist in different hospitals.
- A hospital number cannot be duplicated within the same hospital.
==============================================================================
"""

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.context import (
    RequestContext,
    get_request_context,
)

from app.core.security.authorization import (
    get_authorization_service,
)

from app.core.security.dependencies import (
    get_current_user,
)

from app.db.session import get_db
from app.main import app
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)
from app.modules.patients.services.patient_service import (
    PatientService,
)


@pytest.fixture
def hospital_a_client(
    db: Session,
    hospital,
):
    """
    Create an API client operating as Hospital A.

    These tests focus on tenant isolation, so authentication and
    authorization are explicitly bypassed here.
    """

    def override_get_db():
        yield db

    def override_get_current_user():
        """
        Provide a fake authenticated user.

        Authentication is not under test here.
        """
        return type(
            "TestUser",
            (),
            {
                "id": uuid4(),
                "hospital_id": hospital.id,
            },
        )()

    def override_get_authorization_service():
        """
        Allow the request through authorization so the tests can
        exercise hospital-level isolation.
        """

        class TestAuthorizationService:
            def has_permission(
                self,
                *,
                user_id,
                permission_code,
            ):
                return True

            def has_role(
                self,
                *,
                user_id,
                role_name,
            ):
                return True

        return TestAuthorizationService()

    def override_get_request_context():
        return RequestContext(
            user_id=uuid4(),
            hospital_id=hospital.id,
            permissions=frozenset(
                {
                    "patient.read",
                    "patient.create",
                    "patient.update",
                }
            ),
        )

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    app.dependency_overrides[get_authorization_service] = (
        override_get_authorization_service
    )

    app.dependency_overrides[get_request_context] = (
        override_get_request_context
    )

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def create_patient_for_hospital(
    db: Session,
    hospital_id,
    hospital_number: str,
    first_name: str,
    last_name: str,
):
    """
    Create a patient belonging to a specific hospital.
    """

    service = PatientService(
        repository=PatientRepository(db),
    )

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital_id,
        permissions=frozenset(),
    )

    return service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_number=hospital_number,
            first_name=first_name,
            last_name=last_name,
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )


def test_hospital_cannot_get_another_hospital_patient(
    db,
    hospital,
    hospital_two,
    hospital_a_client,
):
    """
    Hospital A cannot retrieve a patient belonging to Hospital B.
    """

    patient = create_patient_for_hospital(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="HOSP-B-001",
        first_name="John",
        last_name="HospitalB",
    )

    response = hospital_a_client.get(
        f"/api/v1/patients/{patient.id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found."


def test_hospital_cannot_update_another_hospital_patient(
    db,
    hospital,
    hospital_two,
    hospital_a_client,
):
    """
    Hospital A cannot update a patient belonging to Hospital B.
    """

    patient = create_patient_for_hospital(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="HOSP-B-002",
        first_name="Jane",
        last_name="HospitalB",
    )

    response = hospital_a_client.patch(
        f"/api/v1/patients/{patient.id}",
        json={
            "first_name": "Hacked",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found."

    db.refresh(patient)

    assert patient.first_name == "Jane"


def test_hospital_cannot_search_another_hospital_patient(
    db,
    hospital,
    hospital_two,
    hospital_a_client,
):
    """
    Hospital A cannot find a patient belonging to Hospital B through
    patient search.
    """

    patient = create_patient_for_hospital(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="HOSP-B-003",
        first_name="Michael",
        last_name="HospitalB",
    )

    response = hospital_a_client.get(
        "/api/v1/patients",
        params={
            "hospital_number": patient.hospital_number,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 0
    assert body["items"] == []


def test_hospital_can_get_its_own_patient(
    db,
    hospital,
    hospital_a_client,
):
    """
    Hospital A can retrieve its own patient.
    """

    patient = create_patient_for_hospital(
        db=db,
        hospital_id=hospital.id,
        hospital_number="HOSP-A-001",
        first_name="John",
        last_name="HospitalA",
    )

    response = hospital_a_client.get(
        f"/api/v1/patients/{patient.id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(patient.id)
    assert body["hospital_number"] == "HOSP-A-001"


def test_hospital_can_update_its_own_patient(
    db,
    hospital,
    hospital_a_client,
):
    """
    Hospital A can update its own patient.
    """

    patient = create_patient_for_hospital(
        db=db,
        hospital_id=hospital.id,
        hospital_number="HOSP-A-002",
        first_name="Jane",
        last_name="HospitalA",
    )

    response = hospital_a_client.patch(
        f"/api/v1/patients/{patient.id}",
        json={
            "first_name": "Janet",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["first_name"] == "Janet"


def test_hospital_can_search_its_own_patient(
    db,
    hospital,
    hospital_a_client,
):
    """
    Hospital A can search for its own patient.
    """

    patient = create_patient_for_hospital(
        db=db,
        hospital_id=hospital.id,
        hospital_number="HOSP-A-003",
        first_name="Michael",
        last_name="HospitalA",
    )

    response = hospital_a_client.get(
        "/api/v1/patients",
        params={
            "hospital_number": patient.hospital_number,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["id"] == str(patient.id)


def test_same_hospital_number_allowed_in_different_hospitals(
    db,
    hospital,
    hospital_two,
):
    """
    The same hospital number can exist in different hospitals.
    """

    patient_a = create_patient_for_hospital(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PT-000001",
        first_name="John",
        last_name="HospitalA",
    )

    patient_b = create_patient_for_hospital(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="PT-000001",
        first_name="Jane",
        last_name="HospitalB",
    )

    assert patient_a.hospital_id == hospital.id
    assert patient_b.hospital_id == hospital_two.id
    assert patient_a.hospital_number == patient_b.hospital_number


def test_duplicate_hospital_number_rejected_within_same_hospital(
    db,
    hospital,
):
    """
    The same hospital number cannot be registered twice within one hospital.
    """

    create_patient_for_hospital(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PT-000002",
        first_name="John",
        last_name="HospitalA",
    )

    with pytest.raises(HTTPException) as exc_info:
        create_patient_for_hospital(
            db=db,
            hospital_id=hospital.id,
            hospital_number="PT-000002",
            first_name="Jane",
            last_name="HospitalA",
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Hospital number already exists."

    db.rollback()

