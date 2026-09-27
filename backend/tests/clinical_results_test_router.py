from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.modules.clinical_orders.models import ClinicalOrderItem
from app.modules.clinical_results.models import ClinicalResult, ClinicalResultValue

from tests.clinical_orders.test_router import (
    auth_headers,
    authenticate,
    create_doctor_encounter,
    create_hospital,
    create_user,
)


client = TestClient(app)


def _assign_permission(db: Session, user, permission_code: str) -> None:
    from app.modules.identity.models import Permission, Role, RolePermission, UserRole

    permission = (
        db.query(Permission)
        .filter(Permission.code == permission_code)
        .first()
    )
    assert permission is not None, f"Permission not found: {permission_code}"

    role = (
        db.query(Role)
        .filter(
            Role.hospital_id == user.hospital_id,
            Role.name == "Doctor",
        )
        .first()
    )
    assert role is not None

    existing_role_permission = (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
        .first()
    )

    if existing_role_permission is None:
        db.add(
            RolePermission(
                role_id=role.id,
                permission_id=permission.id,
            )
        )

    existing_user_role = (
        db.query(UserRole)
        .filter(
            UserRole.user_account_id == user.id,
            UserRole.role_id == role.id,
        )
        .first()
    )

    if existing_user_role is None:
        db.add(
            UserRole(
                user_account_id=user.id,
                role_id=role.id,
                is_active=True,
            )
        )

    db.commit()


def test_doctor_can_create_custom_laboratory_result(db: Session):
    original_override = app.dependency_overrides.get(get_db)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        hospital = create_hospital(db)

        doctor = create_user(
            db,
            hospital=hospital,
            email=f"doctor-{uuid4()}@example.com",
            role_name="Doctor",
        )

        _assign_permission(
            db,
            doctor,
            "clinical_result.create",
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

        order_payload = {
            "encounter_id": str(encounter.id),
            "order_type": "LABORATORY",
            "priority": "ROUTINE",
            "clinical_indication": "Custom laboratory result API regression test",
            "items": [
                {
                    "custom_name": "Specialized Biomarker X",
                }
            ],
        }

        order_response = client.post(
            "/api/v1/clinical-orders",
            json=order_payload,
            headers=auth_headers(token),
        )

        assert order_response.status_code == 201, order_response.text

        order_data = order_response.json()
        order_item = order_data["items"][0]

        receive_response = client.post(
            f"/api/v1/clinical-orders/items/{order_item["id"]}/receive",
            headers=auth_headers(token),
        )

        assert receive_response.status_code == 200, receive_response.text

        start_response = client.post(
            f"/api/v1/clinical-orders/items/{order_item["id"]}/start",
            headers=auth_headers(token),
        )

        assert start_response.status_code == 200, start_response.text

        started_data = start_response.json()
        started_item = next(
            item
            for item in started_data["items"]
            if item["id"] == order_item["id"]
        )

        assert started_item["status"] == "IN_PROGRESS"

        result_payload = {
            "order_id": order_data["id"],
            "order_item_id": order_item["id"],
            "result_type": "LABORATORY",
            "status": "FINAL",
            "values": [
                {
                    "custom_analyte_name": "Specialized Biomarker X",
                    "custom_analyte_code": "SBX",
                    "custom_unit": "mg/L",
                    "custom_reference_low": 0.5,
                    "custom_reference_high": 2.5,
                    "custom_reference_text": "0.5-2.5 mg/L",
                    "value_numeric": 1.4,
                    "comment": "Custom analyte result",
                }
            ],
        }

        result_response = client.post(
            "/api/v1/clinical-results",
            json=result_payload,
            headers=auth_headers(token),
        )

        assert result_response.status_code == 201, result_response.text

        result_data = result_response.json()

        assert result_data["order_id"] == order_data["id"]
        assert len(result_data["values"]) == 1

        value = result_data["values"][0]

        assert value["analyte_id"] is None
        assert value["analyte_name"] == "Specialized Biomarker X"
        assert value["analyte_code"] == "SBX"
        assert value["custom_analyte_name"] == "Specialized Biomarker X"
        assert value["custom_analyte_code"] == "SBX"
        assert value["custom_unit"] == "mg/L"
        assert value["custom_reference_low"] == 0.5
        assert value["custom_reference_high"] == 2.5
        assert value["custom_reference_text"] == "0.5-2.5 mg/L"
        assert value["value"] == 1.4

        persisted = (
            db.query(ClinicalResultValue)
            .filter(
                ClinicalResultValue.clinical_result_id
                == result_data["id"]
            )
            .one()
        )

        assert persisted.analyte_id is None
        assert persisted.custom_analyte_name == "Specialized Biomarker X"
        assert persisted.custom_analyte_code == "SBX"

    finally:
        if original_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = original_override
