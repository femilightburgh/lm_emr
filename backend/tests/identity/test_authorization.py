"""
========================================================================

LIGHTBURGH EMR

Authorization API Tests

========================================================================

Tests for the administrative authorization workspace.

Coverage includes:

- Administrator access
- Non-administrator access
- User listing
- User lookup
- Hospital tenant isolation
- Role CRUD
- User-role assignment
- User-role removal
- Role permission assignment
- Role permission removal
- Effective permission inheritance

These tests intentionally exercise the real authentication and
authorization dependencies instead of bypassing them.

========================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.context.provider import RequestContextProvider
from app.db.session import get_db
from app.main import app
from app.core.security.authorization_repository import AuthorizationRepository
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
from app.modules.identity.models import (
    Permission,
    Role,
    UserAccount,
    UserRole,
)
from app.modules.identity.permission_repository import (
    PermissionRepository,
)
from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.models import Hospital
from app.modules.organization.schemas import HospitalCreate
from app.modules.organization.service import HospitalService


# ============================================================================
# Test Client
# ============================================================================


@pytest.fixture
def client(db: Session):
    """
    TestClient using the test database.

    Authorization dependencies are intentionally NOT bypassed.
    """

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
    *,
    code: str | None = None,
) -> Hospital:
    """
    Create a unique test hospital.
    """

    hospital_code = (
        code
        or f"AUTHZ-{uuid4().hex[:8].upper()}"
    )

    service = HospitalService(db)

    hospital = service.create_hospital(
        HospitalCreate(
            name=f"Authorization Hospital {hospital_code}",
            code=hospital_code,
            hospital_type=HospitalType.GENERAL,
            ownership=HospitalOwnership.PRIVATE,
            email=f"{hospital_code.lower()}@example.com",
            phone="08000000000",
            address="1 Authorization Street",
            city="Lagos",
            state="Lagos",
        )
    )

    return hospital


def create_user(
    db: Session,
    *,
    hospital: Hospital,
    email: str,
    role_name: str,
    password: str = "password123",
):
    """
    Create a user and assign an initial role.
    """

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
    """
    Authenticate a user and return an access token.
    """

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
    """
    Build an Authorization header.
    """

    return {
        "Authorization": f"Bearer {token}",
    }


def create_role(
    db: Session,
    *,
    hospital: Hospital,
    name: str,
    description: str | None = None,
) -> Role:
    """
    Create a hospital role directly through the service.
    """

    from app.core.context import RequestContext
    from app.modules.identity.role_service import RoleService

    repository = IdentityRepository(db)

    service = RoleService(
        repository=repository,
    )

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    role = service.create_role(
        context=context,
        name=name,
        description=description,
    )

    return role


# ============================================================================
# Administrator Access
# ============================================================================


def test_administrator_can_list_users(
    client,
    db,
):
    """
    An Administrator can access the hospital user list.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin@example.com",
        role_name="Administrator",
    )

    create_user(
        db,
        hospital=hospital,
        email="nurse@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.get(
        "/api/v1/authorization/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    emails = {
        item["email"]
        for item in body
    }

    assert "admin@example.com" in emails
    assert "nurse@example.com" in emails


def test_non_administrator_cannot_list_users(
    client,
    db,
):
    """
    A non-administrator must not access the administrative user list.
    """

    hospital = create_hospital(db)

    receptionist = create_user(
        db,
        hospital=hospital,
        email="receptionist@example.com",
        role_name="Receptionist",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=receptionist.email,
    )

    response = client.get(
        "/api/v1/authorization/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


# ============================================================================
# User Administration
# ============================================================================


def test_administrator_can_get_user(
    client,
    db,
):
    """
    An Administrator can retrieve an individual hospital user.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-get@example.com",
        role_name="Administrator",
    )

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-get@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.get(
        f"/api/v1/authorization/users/{nurse.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(nurse.id)
    assert body["email"] == nurse.email
    assert body["hospital_id"] == str(hospital.id)

    assert len(body["roles"]) == 1
    assert body["roles"][0]["role_name"] == "Nurse"
    assert body["roles"][0]["is_active"] is True


def test_administrator_cannot_get_user_from_another_hospital(
    client,
    db,
):
    """
    An Administrator must not retrieve a user belonging
    to another hospital.
    """

    hospital_one = create_hospital(
        db,
        code=f"AUTHZ-A-{uuid4().hex[:6].upper()}",
    )

    hospital_two = create_hospital(
        db,
        code=f"AUTHZ-B-{uuid4().hex[:6].upper()}",
    )

    admin = create_user(
        db,
        hospital=hospital_one,
        email="admin-isolation@example.com",
        role_name="Administrator",
    )

    other_user = create_user(
        db,
        hospital=hospital_two,
        email="other-hospital@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital_one,
        email=admin.email,
    )

    response = client.get(
        f"/api/v1/authorization/users/{other_user.id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_user_list_is_hospital_scoped(
    client,
    db,
):
    """
    An Administrator must only see users belonging to
    their own hospital.
    """

    hospital_one = create_hospital(
        db,
        code=f"AUTHZ-C-{uuid4().hex[:6].upper()}",
    )

    hospital_two = create_hospital(
        db,
        code=f"AUTHZ-D-{uuid4().hex[:6].upper()}",
    )

    admin = create_user(
        db,
        hospital=hospital_one,
        email="admin-list@example.com",
        role_name="Administrator",
    )

    own_user = create_user(
        db,
        hospital=hospital_one,
        email="own-user@example.com",
        role_name="Nurse",
    )

    foreign_user = create_user(
        db,
        hospital=hospital_two,
        email="foreign-user@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital_one,
        email=admin.email,
    )

    response = client.get(
        "/api/v1/authorization/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    emails = {
        item["email"]
        for item in response.json()
    }

    assert admin.email in emails
    assert own_user.email in emails
    assert foreign_user.email not in emails


# ============================================================================
# Role CRUD
# ============================================================================


def test_administrator_can_create_role(
    client,
    db,
):
    """
    An Administrator can create a hospital role.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-role-create@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json={
            "name": "Clinical Coordinator",
            "description": "Coordinates clinical operations.",
        },
    )
    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Clinical Coordinator"
    assert body["description"] == (
        "Coordinates clinical operations."
    )
    assert body["hospital_id"] == str(hospital.id)
    assert body["is_template"] is False


def test_duplicate_role_is_rejected(
    client,
    db,
):
    """
    A hospital cannot have two roles with the same name.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-role-duplicate@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    payload = {
        "name": "Ward Manager",
        "description": "Ward management.",
    }

    first = client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json=payload,
    )

    assert second.status_code == 409


def test_administrator_can_list_roles(
    client,
    db,
):
    """
    An Administrator can list hospital roles.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-role-list@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json={
            "name": "Senior Nurse",
            "description": "Senior nursing role.",
        },
    )

    client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json={
            "name": "Cashier",
            "description": "Cashier role.",
        },
    )

    response = client.get(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    names = {
        role["name"]
        for role in response.json()
    }

    assert "Administrator" in names
    assert "Senior Nurse" in names
    assert "Cashier" in names


def test_administrator_can_update_role(
    client,
    db,
):
    """
    An Administrator can update a hospital role.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-role-update@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    create_response = client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json={
            "name": "Old Role Name",
            "description": "Old description.",
        },
    )

    assert create_response.status_code == 201

    role_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/authorization/roles/{role_id}",
        headers=auth_headers(token),
        json={
            "name": "New Role Name",
            "description": "New description.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == role_id
    assert body["name"] == "New Role Name"
    assert body["description"] == "New description."


def test_administrator_can_delete_role(
    client,
    db,
):
    """
    An Administrator can delete a hospital role.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-role-delete@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    create_response = client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json={
            "name": "Temporary Role",
            "description": None,
        },
    )

    assert create_response.status_code == 201

    role_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/authorization/roles/{role_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/authorization/roles/{role_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


# ============================================================================
# User Role Assignment
# ============================================================================


def test_administrator_can_assign_role_to_user(
    client,
    db,
):
    """
    An Administrator can assign an additional role to a user.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-assign@example.com",
        role_name="Administrator",
    )

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-assign@example.com",
        role_name="Nurse",
    )

    create_role(
        db,
        hospital=hospital,
        name="Ward Manager",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.post(
        f"/api/v1/authorization/users/{nurse.id}/roles",
        headers=auth_headers(token),
        json={
            "role_name": "Ward Manager",
        },
    )

    assert response.status_code == 204

    user_response = client.get(
        f"/api/v1/authorization/users/{nurse.id}",
        headers=auth_headers(token),
    )

    assert user_response.status_code == 200

    role_names = {
        role["role_name"]
        for role in user_response.json()["roles"]
    }

    assert "Nurse" in role_names
    assert "Ward Manager" in role_names


def test_assigning_existing_active_role_is_rejected(
    client,
    db,
):
    """
    An active duplicate user-role assignment must be rejected.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-duplicate-role@example.com",
        role_name="Administrator",
    )

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-duplicate-role@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.post(
        f"/api/v1/authorization/users/{nurse.id}/roles",
        headers=auth_headers(token),
        json={
            "role_name": "Nurse",
        },
    )

    assert response.status_code == 409


def test_administrator_can_remove_role_from_user(
    client,
    db,
):
    """
    Removing a role deactivates the UserRole assignment.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-remove-role@example.com",
        role_name="Administrator",
    )

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-remove-role@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.delete(
        f"/api/v1/authorization/users/{nurse.id}/roles/Nurse",
        headers=auth_headers(token),
    )

    assert response.status_code == 204

    user_response = client.get(
        f"/api/v1/authorization/users/{nurse.id}",
        headers=auth_headers(token),
    )

    assert user_response.status_code == 200

    role_names = {
        role["role_name"]
        for role in user_response.json()["roles"]
    }

    assert "Nurse" not in role_names


def test_removed_role_can_be_reactivated(
    client,
    db,
):
    """
    A previously inactive UserRole assignment is reactivated
    rather than duplicated.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-reactivate@example.com",
        role_name="Administrator",
    )

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-reactivate@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    remove_response = client.delete(
        f"/api/v1/authorization/users/{nurse.id}/roles/Nurse",
        headers=auth_headers(token),
    )

    assert remove_response.status_code == 204

    assign_response = client.post(
        f"/api/v1/authorization/users/{nurse.id}/roles",
        headers=auth_headers(token),
        json={
            "role_name": "Nurse",
        },
    )

    assert assign_response.status_code == 204

    user_response = client.get(
        f"/api/v1/authorization/users/{nurse.id}",
        headers=auth_headers(token),
    )

    assert user_response.status_code == 200

    roles = user_response.json()["roles"]

    nurse_roles = [
        role
        for role in roles
        if role["role_name"] == "Nurse"
    ]

    assert len(nurse_roles) == 1
    assert nurse_roles[0]["is_active"] is True


def test_administrator_cannot_assign_role_to_foreign_hospital_user(
    client,
    db,
):
    """
    A hospital administrator cannot assign a role to a user
    belonging to another hospital.
    """

    hospital_one = create_hospital(
        db,
        code=f"AUTHZ-E-{uuid4().hex[:6].upper()}",
    )

    hospital_two = create_hospital(
        db,
        code=f"AUTHZ-F-{uuid4().hex[:6].upper()}",
    )

    admin = create_user(
        db,
        hospital=hospital_one,
        email="admin-cross-user@example.com",
        role_name="Administrator",
    )

    foreign_user = create_user(
        db,
        hospital=hospital_two,
        email="foreign-role-user@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital_one,
        email=admin.email,
    )

    response = client.post(
        f"/api/v1/authorization/users/{foreign_user.id}/roles",
        headers=auth_headers(token),
        json={
            "role_name": "Nurse",
        },
    )

    assert response.status_code == 404


# ============================================================================
# Role Permissions
# ============================================================================


def test_administrator_can_assign_permission_to_role(
    client,
    db,
):
    """
    An Administrator can assign a platform permission to a role.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-permission@example.com",
        role_name="Administrator",
    )

    create_role(
        db,
        hospital=hospital,
        name="Vitals Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.get(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    role = next(
        role
        for role in response.json()
        if role["name"] == "Vitals Nurse"
    )

    role_id = role["id"]

    permission_code = "vitals.create"

    response = client.post(
        f"/api/v1/authorization/roles/{role_id}/permissions",
        headers=auth_headers(token),
        json={
            "permission_code": permission_code,
        },
    )

    assert response.status_code == 204

    permissions_response = client.get(
        f"/api/v1/authorization/roles/{role_id}/permissions",
        headers=auth_headers(token),
    )

    assert permissions_response.status_code == 200

    permission_codes = {
        permission["code"]
        for permission
        in permissions_response.json()["permissions"]
    }

    assert permission_code in permission_codes


def test_administrator_can_remove_permission_from_role(
    client,
    db,
):
    """
    An Administrator can remove a permission from a role.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-remove-permission@example.com",
        role_name="Administrator",
    )

    create_role(
        db,
        hospital=hospital,
        name="Vitals Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    roles_response = client.get(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
    )

    role = next(
        role
        for role in roles_response.json()
        if role["name"] == "Vitals Nurse"
    )

    role_id = role["id"]
    permission_code = "vitals.create"

    assign_response = client.post(
        f"/api/v1/authorization/roles/{role_id}/permissions",
        headers=auth_headers(token),
        json={
            "permission_code": permission_code,
        },
    )

    assert assign_response.status_code == 204

    remove_response = client.delete(
        f"/api/v1/authorization/roles/{role_id}/permissions/"
        f"{permission_code}",
        headers=auth_headers(token),
    )

    assert remove_response.status_code == 204

    permissions_response = client.get(
        f"/api/v1/authorization/roles/{role_id}/permissions",
        headers=auth_headers(token),
    )

    assert permissions_response.status_code == 200

    permission_codes = {
        permission["code"]
        for permission
        in permissions_response.json()["permissions"]
    }

    assert permission_code not in permission_codes


def test_non_administrator_cannot_manage_role_permissions(
    client,
    db,
):
    """
    A non-administrator cannot modify role permissions.
    """

    hospital = create_hospital(db)

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-permission-denied@example.com",
        role_name="Nurse",
    )

    role = create_role(
        db,
        hospital=hospital,
        name="Restricted Role",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=nurse.email,
    )

    response = client.post(
        f"/api/v1/authorization/roles/{role.id}/permissions",
        headers=auth_headers(token),
        json={
            "permission_code": "vitals.create",
        },
    )

    assert response.status_code == 403


def test_non_administrator_cannot_manage_roles(
    client,
    db,
):
    """
    A non-administrator cannot create or delete roles.
    """

    hospital = create_hospital(db)

    nurse = create_user(
        db,
        hospital=hospital,
        email="nurse-role-denied@example.com",
        role_name="Nurse",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=nurse.email,
    )

    create_response = client.post(
        "/api/v1/authorization/roles",
        headers=auth_headers(token),
        json={
            "name": "Unauthorized Role",
            "description": None,
        },
    )

    assert create_response.status_code == 403


# ============================================================================
# Cross-Hospital Role Isolation
# ============================================================================


def test_administrator_cannot_modify_foreign_role(
    client,
    db,
):
    """
    An Administrator from Hospital A must not be able to update
    or delete a role belonging to Hospital B.
    """

    hospital_one = create_hospital(
        db,
        code=f"AUTHZ-G-{uuid4().hex[:6].upper()}",
    )

    hospital_two = create_hospital(
        db,
        code=f"AUTHZ-H-{uuid4().hex[:6].upper()}",
    )

    admin = create_user(
        db,
        hospital=hospital_one,
        email="admin-cross-role@example.com",
        role_name="Administrator",
    )

    foreign_role = create_role(
        db,
        hospital=hospital_two,
        name="Foreign Role",
    )

    token = authenticate(
        db,
        hospital=hospital_one,
        email=admin.email,
    )

    update_response = client.put(
        f"/api/v1/authorization/roles/{foreign_role.id}",
        headers=auth_headers(token),
        json={
            "name": "Hijacked Role",
            "description": None,
        },
    )

    assert update_response.status_code == 404

    delete_response = client.delete(
        f"/api/v1/authorization/roles/{foreign_role.id}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code == 404


# ============================================================================
# Effective Permission Inheritance
# ============================================================================


def test_user_inherits_permission_from_role(
    db,
):
    """
    A user's effective permissions are inherited through:

        UserRole
            ↓
        RolePermission
            ↓
        Permission
    """

    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email="permission-user@example.com",
        role_name="Nurse",
    )

    repository = IdentityRepository(db)

    role = repository.get_role_by_name(
        hospital_id=hospital.id,
        role_name="Nurse",
    )

    assert role is not None

    permission = (
        db.query(Permission)
        .filter(
            Permission.code == "vitals.create",
        )
        .one_or_none()
    )

    assert permission is not None

    role_permission_repository = RolePermissionRepository(
        db,
    )

    role_permission_service = RolePermissionService(
        repository=role_permission_repository,
        permission_repository=__import__(
            "app.modules.identity.permission_repository",
            fromlist=["PermissionRepository"],
        ).PermissionRepository(db),
    )

    role_permission_service.assign_permission(
        role_id=role.id,
        permission_code="vitals.create",
    )

    db.commit()

    permission_codes = repository.get_user_permission_codes(
        user.id,
    )

    assert "vitals.create" in permission_codes


def test_inactive_role_no_longer_grants_permission(
    db,
):
    """
    Removing an active role must remove its inherited permissions
    from the user's effective permission set.
    """

    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email="inactive-role-user@example.com",
        role_name="Nurse",
    )

    repository = IdentityRepository(db)

    role = repository.get_role_by_name(
        hospital_id=hospital.id,
        role_name="Nurse",
    )

    assert role is not None

    permission_repository = __import__(
        "app.modules.identity.permission_repository",
        fromlist=["PermissionRepository"],
    ).PermissionRepository(db)

    permission_service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=permission_repository,
    )

    permission_service.assign_permission(
        role_id=role.id,
        permission_code="vitals.create",
    )

    db.commit()

    before = repository.get_user_permission_codes(
        user.id,
    )

    assert "vitals.create" in before

    user_role = repository.get_user_role(
        user_id=user.id,
        role_id=role.id,
    )

    assert user_role is not None

    repository.deactivate_user_role(
        user_role,
    )

    db.commit()

    after = repository.get_user_permission_codes(
        user.id,
    )

    assert "vitals.create" not in after


def test_administrator_can_onboard_staff(
    client,
    db,
):
    """
    An Administrator can onboard a staff member.

    The new account must be pending, receive its initial role,
    and have an activation invitation.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-onboard@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    response = client.post(
        "/api/v1/authorization/users/onboard",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "email": "new-nurse@example.com",
            "role_name": "Nurse",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user"]["email"] == (
        "new-nurse@example.com"
    )

    assert data["user"]["status"] == "PENDING"

    assert any(
        role["role_name"] == "Nurse"
        for role in data["user"]["roles"]
    )

    assert data["invitation_token"]
    assert data["invitation_expires_at"]

    repository = IdentityRepository(db)

    user = repository.get_user_by_email(
        hospital_id=hospital.id,
        email="new-nurse@example.com",
    )

    assert user is not None
    assert user.status.value == "PENDING"


def test_staff_activation_completes_onboarding(
    client,
    db,
):
    """
    A pending staff member can activate their account using
    the invitation token, establish a password, and then log in.

    The invitation cannot be reused.
    """

    hospital = create_hospital(db)

    admin = create_user(
        db,
        hospital=hospital,
        email="admin-activation@example.com",
        role_name="Administrator",
    )

    token = authenticate(
        db,
        hospital=hospital,
        email=admin.email,
    )

    onboarding_response = client.post(
        "/api/v1/authorization/users/onboard",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "email": "activation-nurse@example.com",
            "role_name": "Nurse",
        },
    )

    assert onboarding_response.status_code == 201

    invitation_token = (
        onboarding_response.json()["invitation_token"]
    )

    activation_response = client.post(
        "/api/v1/auth/activate",
        json={
            "token": invitation_token,
            "password": "NewSecurePassword123!",
        },
    )

    assert activation_response.status_code == 204

    repository = IdentityRepository(db)

    user = repository.get_user_by_email(
        hospital_id=hospital.id,
        email="activation-nurse@example.com",
    )

    assert user is not None
    assert user.status.value == "ACTIVE"

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "hospital_code": hospital.code,
            "email": "activation-nurse@example.com",
            "password": "NewSecurePassword123!",
        },
    )

    assert login_response.status_code == 200

    reuse_response = client.post(
        "/api/v1/auth/activate",
        json={
            "token": invitation_token,
            "password": "AnotherPassword123!",
        },
    )

    assert reuse_response.status_code == 400

# ============================================================================
# Tenant and Expiry Authorization Regression Tests
# ============================================================================


def _assign_permission_to_role(db, role_id, permission_code):
    service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )
    service.assign_permission(
        role_id=role_id,
        permission_code=permission_code,
    )
    db.commit()


def test_cross_hospital_role_assignment_grants_no_access(db):
    """
    A malformed cross-hospital UserRole assignment must not grant
    role or permission access through any effective-permission path.
    """
    hospital_one = create_hospital(
        db, code=f"AUTHZ-XA-{uuid4().hex[:6].upper()}"
    )
    hospital_two = create_hospital(
        db, code=f"AUTHZ-XB-{uuid4().hex[:6].upper()}"
    )

    user = create_user(
        db,
        hospital=hospital_one,
        email=f"cross-user-{uuid4().hex[:8]}@example.com",
        role_name="Receptionist",
    )

    foreign_role = create_role(
        db,
        hospital=hospital_two,
        name=f"ForeignRole-{uuid4().hex[:8]}",
        description="Cross-hospital authorization regression role",
    )

    _assign_permission_to_role(db, foreign_role.id, "vitals.create")

    # Deliberately create an invalid cross-hospital assignment to verify
    # runtime defenses even if bad data enters the database.
    db.add(
        UserRole(
            user_account_id=user.id,
            role_id=foreign_role.id,
            is_active=True,
        )
    )
    db.commit()
    db.expire_all()

    identity_repository = IdentityRepository(db)
    authorization_repository = AuthorizationRepository(db)

    assert not authorization_repository.role_exists_for_user(
        user_id=user.id,
        role_name=foreign_role.name,
    )
    assert not authorization_repository.permission_exists_for_user(
        user_id=user.id,
        permission_code="vitals.create",
    )

    assert foreign_role.name not in identity_repository.get_user_role_names(
        user.id
    )
    assert not identity_repository.user_has_role(
        user_id=user.id,
        role_name=foreign_role.name,
    )
    assert "vitals.create" not in identity_repository.get_user_permission_codes(
        user.id
    )

    reloaded_user = db.get(UserAccount, user.id)
    assert reloaded_user is not None
    context = RequestContextProvider().build(user=reloaded_user)
    assert "vitals.create" not in context.permissions


def test_expired_role_assignment_grants_no_permission(db):
    """
    An expired role assignment must not grant permissions through
    authorization queries or request-context construction.
    """
    hospital = create_hospital(
        db, code=f"AUTHZ-EX-{uuid4().hex[:8].upper()}"
    )

    user = create_user(
        db,
        hospital=hospital,
        email=f"expired-user-{uuid4().hex[:8]}@example.com",
        role_name="Receptionist",
    )

    role = create_role(
        db,
        hospital=hospital,
        name=f"ExpiredRole-{uuid4().hex[:8]}",
        description="Expired authorization regression role",
    )

    _assign_permission_to_role(db, role.id, "vitals.create")

    assignment = UserRole(
        user_account_id=user.id,
        role_id=role.id,
        is_active=True,
        expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )
    db.add(assignment)
    db.commit()
    db.expire_all()

    identity_repository = IdentityRepository(db)
    authorization_repository = AuthorizationRepository(db)

    assert not authorization_repository.role_exists_for_user(
        user_id=user.id,
        role_name=role.name,
    )
    assert not authorization_repository.permission_exists_for_user(
        user_id=user.id,
        permission_code="vitals.create",
    )

    assert not identity_repository.user_has_role(
        user_id=user.id,
        role_name=role.name,
    )
    assert "vitals.create" not in identity_repository.get_user_permission_codes(
        user.id
    )

    reloaded_user = db.get(UserAccount, user.id)
    assert reloaded_user is not None
    context = RequestContextProvider().build(user=reloaded_user)
    assert "vitals.create" not in context.permissions
