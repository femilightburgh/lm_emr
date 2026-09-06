from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.models import TerminologyConcept, TerminologySynonym

from tests.clinical_orders.test_router import (
    authenticate,
    auth_headers,
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


@pytest.fixture(autouse=True)
def clean_terminology(db):
    db.execute(TerminologySynonym.__table__.delete())
    db.execute(TerminologyConcept.__table__.delete())
    db.commit()


def seed_concept(
    db: Session,
    *,
    code: str,
    display_name: str,
    synonyms: tuple[str, ...] = (),
):
    concept = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=code,
        display_name=display_name,
        active=True,
        release_version="TEST",
        is_leaf=True,
        is_residual=False,
    )

    db.add(concept)
    db.flush()

    for term in synonyms:
        db.add(
            TerminologySynonym(
                concept_id=concept.id,
                term=term,
            )
        )

    db.commit()
    db.refresh(concept)

    return concept


def test_search_diagnoses_endpoint_by_name(
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

    concept = seed_concept(
        db,
        code="TEST-I10",
        display_name="Essential (primary) hypertension",
        synonyms=("Hypertension",),
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        params={"q": "hypertension"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(concept.id)
    assert body[0]["system"] == "ICD-10-CM"
    assert body[0]["code"] == "TEST-I10"
    assert body[0]["display_name"] == (
        "Essential (primary) hypertension"
    )


def test_search_diagnoses_endpoint_by_code(
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

    concept = seed_concept(
        db,
        code="TEST-I10",
        display_name="Essential (primary) hypertension",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        params={"q": "TEST-I10"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["id"] for item in body] == [
        str(concept.id),
    ]


def test_search_diagnoses_endpoint_filters_system(
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

    concept = seed_concept(
        db,
        code="TEST-I10",
        display_name="Essential (primary) hypertension",
    )

    other = TerminologyConcept(
        system=TerminologySystem.SNOMED_CT,
        code="TEST-38341003",
        display_name="Hypertensive disorder",
        active=True,
        release_version="TEST",
        is_leaf=True,
        is_residual=False,
    )

    db.add(other)
    db.commit()

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        params={
            "q": "hypertension",
            "system": "ICD-10-CM",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["id"] for item in body] == [
        str(concept.id),
    ]


def test_search_diagnoses_endpoint_returns_icd11_leaf_concepts(
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

    leaf = TerminologyConcept(
        system=TerminologySystem.ICD_11,
        code="1A00",
        display_name="Cholera",
        active=True,
        release_version="TEST",
        is_leaf=True,
        is_residual=False,
    )

    non_leaf = TerminologyConcept(
        system=TerminologySystem.ICD_11,
        code="1A00-GROUP",
        display_name="Cholera group",
        active=True,
        release_version="TEST",
        is_leaf=False,
        is_residual=False,
    )

    db.add_all([leaf, non_leaf])
    db.commit()

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        params={
            "q": "cholera",
            "system": "ICD-11",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["id"] for item in body] == [
        str(leaf.id),
    ]
    assert body[0]["system"] == "ICD-11"
    assert body[0]["code"] == "1A00"
    assert body[0]["display_name"] == "Cholera"


def test_search_diagnoses_endpoint_returns_icd11_leaf_concepts(
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

    leaf = TerminologyConcept(
        system=TerminologySystem.ICD_11,
        code="1A00",
        display_name="Cholera",
        active=True,
        release_version="TEST",
        is_leaf=True,
        is_residual=False,
    )

    non_leaf = TerminologyConcept(
        system=TerminologySystem.ICD_11,
        code="1A00-GROUP",
        display_name="Cholera group",
        active=True,
        release_version="TEST",
        is_leaf=False,
        is_residual=False,
    )

    db.add_all([leaf, non_leaf])
    db.commit()

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        params={
            "q": "cholera",
            "system": "ICD-11",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["id"] for item in body] == [
        str(leaf.id),
    ]
    assert body[0]["system"] == "ICD-11"
    assert body[0]["code"] == "1A00"
    assert body[0]["display_name"] == "Cholera"


def test_search_diagnoses_requires_permission(
    client,
    db,
):
    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email=f"reception-{uuid4()}@example.com",
        role_name="Receptionist",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        params={"q": "hypertension"},
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_search_diagnoses_rejects_missing_query(
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

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    response = client.get(
        "/api/v1/terminology/diagnoses/search",
        headers=auth_headers(token),
    )

    assert response.status_code == 422
