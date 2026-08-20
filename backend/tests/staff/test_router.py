import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from uuid import uuid4


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    from app.modules.staff.router import router as staff_router

    for route in staff_router.routes:
        for dependency in route.dependant.dependencies:
            dependency_name = getattr(
                dependency.call,
                "__name__",
                "",
            )

            if dependency_name == "dependency":
                app.dependency_overrides[dependency.call] = (
                    lambda: None
                )

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_create_staff_endpoint(client, hospital):
    response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-001",
            "first_name": "John",
            "last_name": "Doe",
            "gender": "Male",
            "date_of_birth": "1990-01-15",
            "phone_number": "08000000000",
            "email": "john.doe@example.com",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
            "date_left": None,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["hospital_id"] == str(hospital.id)
    assert body["staff_number"] == "API-001"
    assert body["first_name"] == "John"
    assert body["middle_name"] is None
    assert body["last_name"] == "Doe"
    assert body["gender"] == "Male"
    assert body["date_of_birth"] == "1990-01-15"
    assert body["phone_number"] == "08000000000"
    assert body["user_account_id"] is None
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_get_staff_endpoint(client, hospital):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-002",
            "first_name": "Jane",
            "last_name": "Doe",
            "gender": "Female",
            "date_of_birth": "1992-05-10",
            "profession": "Nurse",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-02-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/staff/{staff_id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == staff_id
    assert body["hospital_id"] == str(hospital.id)
    assert body["staff_number"] == "API-002"
    assert body["first_name"] == "Jane"
    assert body["last_name"] == "Doe"
    assert body["gender"] == "Female"

def test_list_staff_endpoint(client, hospital):
    for staff_number, first_name, last_name in [
        ("API-003", "Alice", "Brown"),
        ("API-004", "Bob", "Smith"),
    ]:
        response = client.post(
            "/api/v1/staff",
            json={
                "hospital_id": str(hospital.id),
                "staff_number": staff_number,
                "first_name": first_name,
                "last_name": last_name,
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "profession": "Doctor",
                "employment_status": "Active",
                "employment_type": "Full Time",
                "date_employed": "2026-01-01",
            },
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/staff",
        params={"hospital_id": str(hospital.id)},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert len(body["items"]) == 2

    assert body["items"][0]["staff_number"] == "API-003"
    assert body["items"][1]["staff_number"] == "API-004"

def test_update_staff_endpoint(client, hospital):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-005",
            "first_name": "Michael",
            "last_name": "Brown",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/staff/{staff_id}",
        json={
            "first_name": "Michael",
            "last_name": "Johnson",
            "phone_number": "08011111111",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == staff_id
    assert body["first_name"] == "Michael"
    assert body["last_name"] == "Johnson"
    assert body["phone_number"] == "08011111111"


def test_link_user_account_endpoint(
    client,
    hospital,
    db,
):
    from tests.identity.test_authorization import (
        create_role,
        create_user,
    )

    create_role(
        db,
        hospital=hospital,
        name="Receptionist",
    )

    user = create_user(
        db,
        hospital=hospital,
        email="receptionist@example.com",
        role_name="Receptionist",
    )

    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "LINK-001",
            "first_name": "Reception",
            "last_name": "Staff",
            "gender": "Female",
            "date_of_birth": "1990-01-01",
            "email": "receptionist@example.com",
            "profession": "Nurse",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/staff/{staff_id}/link-user",
        json={
            "user_account_id": str(user.id),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == staff_id
    assert body["user_account_id"] == str(user.id)


def test_link_user_account_rejects_foreign_hospital(
    client,
    hospital,
    db,
):
    from tests.identity.test_authorization import (
        create_hospital,
        create_user,
    )

    foreign_hospital = create_hospital(
        db,
        code=f"FOREIGN-LINK-{uuid4().hex[:6].upper()}",
    )

    foreign_user = create_user(
        db,
        hospital=foreign_hospital,
        email="foreign-receptionist@example.com",
        role_name="Receptionist",
    )

    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "LINK-002",
            "first_name": "Foreign",
            "last_name": "Link",
            "gender": "Female",
            "date_of_birth": "1990-01-01",
            "profession": "Nurse",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/staff/{staff_id}/link-user",
        json={
            "user_account_id": str(foreign_user.id),
        },
    )

    assert response.status_code == 400


def test_list_employment_history_endpoint(client, hospital):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-006",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "gender": "Female",
            "date_of_birth": "1991-07-12",
            "profession": "Nurse",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2023-06-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/staff/{staff_id}/employments",
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1

    employment = body[0]

    assert employment["staff_id"] == staff_id
    assert employment["profession"] == "Nurse"
    assert employment["employment_status"] == "Active"
    assert employment["employment_type"] == "Full Time"
    assert employment["date_employed"] == "2023-06-01"
    assert employment["date_left"] is None


def test_get_current_employment_endpoint(client, hospital):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-007",
            "first_name": "David",
            "last_name": "Smith",
            "gender": "Male",
            "date_of_birth": "1988-03-20",
            "profession": "Pharmacist",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2024-01-15",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/staff/{staff_id}/employments/current",
    )

    assert response.status_code == 200

    body = response.json()

    assert body is not None
    assert body["staff_id"] == staff_id
    assert body["profession"] == "Pharmacist"
    assert body["employment_status"] == "Active"
    assert body["employment_type"] == "Full Time"
    assert body["date_employed"] == "2024-01-15"
    assert body["date_left"] is None

def test_close_current_employment_endpoint(client, hospital):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-008",
            "first_name": "David",
            "last_name": "Williams",
            "gender": "Male",
            "date_of_birth": "1985-09-05",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2020-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/staff/{staff_id}/employments/current",
        json={
            "date_left": "2026-08-01",
            "employment_status": "Resigned",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["staff_id"] == staff_id
    assert body["date_employed"] == "2020-01-01"
    assert body["date_left"] == "2026-08-01"
    assert body["employment_status"] == "Resigned"

def test_closed_employment_is_no_longer_current_endpoint(
    client,
    hospital,
):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-009",
            "first_name": "Robert",
            "last_name": "Williams",
            "gender": "Male",
            "date_of_birth": "1985-09-05",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2020-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    close_response = client.patch(
        f"/api/v1/staff/{staff_id}/employments/current",
        json={
            "date_left": "2026-08-01",
            "employment_status": "Resigned",
        },
    )

    assert close_response.status_code == 200

    response = client.get(
        f"/api/v1/staff/{staff_id}/employments/current",
    )

    assert response.status_code == 200
    assert response.json() is None

def test_start_employment_endpoint(client, hospital):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-010",
            "first_name": "James",
            "last_name": "Brown",
            "gender": "Male",
            "date_of_birth": "1990-04-10",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2020-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    close_response = client.patch(
        f"/api/v1/staff/{staff_id}/employments/current",
        json={
            "date_left": "2026-08-01",
            "employment_status": "Resigned",
        },
    )

    assert close_response.status_code == 200

    response = client.post(
        f"/api/v1/staff/{staff_id}/employments",
        json={
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-09-01",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["staff_id"] == staff_id
    assert body["profession"] == "Doctor"
    assert body["employment_status"] == "Active"
    assert body["employment_type"] == "Full Time"
    assert body["date_employed"] == "2026-09-01"
    assert body["date_left"] is None

def test_get_staff_returns_404_for_nonexistent_staff(client):
    staff_id = uuid4()

    response = client.get(
        f"/api/v1/staff/{staff_id}",
    )

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "STAFF_NOT_FOUND"
    assert body["error"]["message"] == (
        f"Staff '{staff_id}' was not found."
    )
    assert body["path"] == f"/api/v1/staff/{staff_id}"

def test_create_staff_returns_409_for_duplicate_staff_number(
    client,
    hospital,
):
    payload = {
        "hospital_id": str(hospital.id),
        "staff_number": "API-011",
        "first_name": "Alice",
        "last_name": "Brown",
        "gender": "Female",
        "date_of_birth": "1990-01-01",
        "profession": "Doctor",
        "employment_status": "Active",
        "employment_type": "Full Time",
        "date_employed": "2026-01-01",
    }

    first_response = client.post(
        "/api/v1/staff",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/staff",
        json=payload,
    )

    assert second_response.status_code == 409

    body = second_response.json()

    assert body["error"]["code"] == "DUPLICATE_STAFF_NUMBER"


def test_create_staff_returns_404_for_nonexistent_hospital(client):
    from uuid import uuid4

    hospital_id = uuid4()

    response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital_id),
            "staff_number": "API-012",
            "first_name": "Peter",
            "last_name": "Brown",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "HOSPITAL_NOT_FOUND"

def test_create_staff_returns_400_for_invalid_employment_date(
    client,
    hospital,
):
    response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-013",
            "first_name": "Daniel",
            "last_name": "Brown",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "1989-01-01",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["code"] == "APPLICATION_ERROR"

def test_start_employment_returns_400_when_current_employment_exists(
    client,
    hospital,
):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-014",
            "first_name": "Thomas",
            "last_name": "Brown",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/staff/{staff_id}/employments",
        json={
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-02-01",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["code"] == "APPLICATION_ERROR"

def test_close_current_employment_returns_400_when_none_exists(
    client,
    hospital,
):
    create_response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            "staff_number": "API-015",
            "first_name": "Grace",
            "last_name": "Brown",
            "gender": "Female",
            "date_of_birth": "1990-01-01",
            "profession": "Nurse",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2020-01-01",
        },
    )

    assert create_response.status_code == 201

    staff_id = create_response.json()["id"]

    first_close = client.patch(
        f"/api/v1/staff/{staff_id}/employments/current",
        json={
            "date_left": "2026-01-01",
            "employment_status": "Resigned",
        },
    )

    assert first_close.status_code == 200

    second_close = client.patch(
        f"/api/v1/staff/{staff_id}/employments/current",
        json={
            "date_left": "2026-02-01",
            "employment_status": "Resigned",
        },
    )

    assert second_close.status_code == 400

    body = second_close.json()

    assert body["error"]["code"] == "APPLICATION_ERROR"

def test_create_staff_returns_422_for_invalid_hospital_id(
    client,
):
    response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": "not-a-uuid",
            "staff_number": "API-016",
            "first_name": "John",
            "last_name": "Doe",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert response.status_code == 422

def test_create_staff_returns_422_when_required_field_is_missing(
    client,
    hospital,
):
    response = client.post(
        "/api/v1/staff",
        json={
            "hospital_id": str(hospital.id),
            # staff_number intentionally omitted
            "first_name": "John",
            "last_name": "Doe",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "profession": "Doctor",
            "employment_status": "Active",
            "employment_type": "Full Time",
            "date_employed": "2026-01-01",
        },
    )

    assert response.status_code == 422