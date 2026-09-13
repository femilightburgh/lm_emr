from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app

from app.modules.diagnoses.enums import (
    DiagnosisCertainty,
    DiagnosisType,
)
from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.models import TerminologyConcept
from app.modules.events.enums import EventType
from app.modules.events.models import ClinicalEvent

from tests.clinical_orders.test_router import (
    authenticate,
    auth_headers,
    create_doctor_encounter,
    create_hospital,
    create_user,
)


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def seed_terminology_concept(
    db,
    *,
    code: str,
    display_name: str,
):
    concept = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=code,
        display_name=display_name,
        release_version="2026 Jan",
        is_leaf=True,
        is_residual=False,
        active=True,
    )

    db.add(concept)
    db.commit()
    db.refresh(concept)

    return concept


def test_create_diagnosis_endpoint(
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

    seed_terminology_concept(
        db,
        code="I10",
        display_name="Essential (primary) hypertension",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.post(
        "/api/v1/diagnoses",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "diagnosis_name": "Essential hypertension",
            "code_system": "ICD-10-CM",
            "code": "I10",
            "diagnosis_type": "FINAL",
            "certainty": "CONFIRMED",
            "onset_date": "2026-08-01",
            "notes": "Persistent elevated blood pressure.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["encounter_id"] == str(encounter.id)
    assert body["episode_id"] == str(encounter.episode_id)
    assert body["diagnosis_name"] == (
        "Essential (primary) hypertension"
    )
    assert body["code_system"] == "ICD-10-CM"
    assert body["code"] == "I10"
    assert body["diagnosis_type"] == "FINAL"
    assert body["certainty"] == "CONFIRMED"
    assert body["onset_date"] == "2026-08-01"
    assert body["diagnosed_by"] == str(staff.id)

    event = (
        db.query(ClinicalEvent)
        .filter(
            ClinicalEvent.encounter_id == encounter.id,
            ClinicalEvent.event_type == EventType.DIAGNOSIS_RECORDED,
        )
        .one()
    )

    assert event.performed_by == staff.id
    assert event.payload["clinical_diagnosis_id"] == body["id"]
    assert event.payload["code"] == "I10"


def test_get_diagnosis_endpoint(
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

    seed_terminology_concept(
        db,
        code="G43.009",
        display_name="Migraine without aura",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    create_response = client.post(
        "/api/v1/diagnoses",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "diagnosis_name": "Migraine without aura",
            "code_system": "ICD-10-CM",
            "code": "G43.009",
            "diagnosis_type": "PROVISIONAL",
            "certainty": "SUSPECTED",
        },
    )

    assert create_response.status_code == 201

    diagnosis_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/diagnoses/{diagnosis_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == diagnosis_id
    assert body["encounter_id"] == str(encounter.id)
    assert body["diagnosis_name"] == "Migraine without aura"


def test_list_encounter_diagnoses_endpoint(
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

    for diagnosis_name in (
        "Headache",
        "Migraine",
    ):
        response = client.post(
            "/api/v1/diagnoses",
            headers=auth_headers(token),
            json={
                "encounter_id": str(encounter.id),
                "diagnosis_name": diagnosis_name,
                "diagnosis_type": "PROVISIONAL",
                "certainty": "POSSIBLE",
            },
        )

        assert response.status_code == 201

    response = client.get(
        f"/api/v1/diagnoses/encounters/{encounter.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["diagnosis_name"] for item in body] == [
        "Headache",
        "Migraine",
    ]


def test_create_diagnosis_requires_permission(
    client,
    db,
):
    hospital = create_hospital(db)

    receptionist = create_user(
        db,
        hospital=hospital,
        email=f"reception-{uuid4()}@example.com",
        role_name="Receptionist",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=receptionist.email,
    )

    response = client.post(
        "/api/v1/diagnoses",
        headers=auth_headers(token),
        json={
            "encounter_id": str(uuid4()),
            "diagnosis_name": "Hypertension",
            "diagnosis_type": "PROVISIONAL",
            "certainty": "SUSPECTED",
        },
    )

    assert response.status_code == 403


def test_create_diagnosis_rejects_closed_encounter(
    client,
    db,
):
    from app.modules.encounter.models import EncounterStatus

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

    encounter.status = EncounterStatus.CLOSED
    db.commit()

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.post(
        "/api/v1/diagnoses",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "diagnosis_name": "Hypertension",
            "diagnosis_type": "PROVISIONAL",
            "certainty": "SUSPECTED",
        },
    )

    assert response.status_code == 409


def test_create_diagnosis_rejects_invalid_payload(
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

    response = client.post(
        "/api/v1/diagnoses",
        headers=auth_headers(token),
        json={
            "encounter_id": str(encounter.id),
            "diagnosis_name": "",
            "diagnosis_type": "PROVISIONAL",
            "certainty": "SUSPECTED",
        },
    )

    assert response.status_code == 422
