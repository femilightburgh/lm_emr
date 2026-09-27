from uuid import uuid4

import jwt
import pytest

from app.modules.identity.auth_service import AuthService
from app.modules.identity.exceptions import (
    ExpiredTokenError,
    InactiveAccountError,
    InvalidTokenError,
)
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.token_service import TokenService
from app.modules.identity.user_service import UserService
from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.schemas import HospitalCreate
from app.modules.organization.service import HospitalService


# =============================================================================
# Helpers
# =============================================================================


def create_receptionist(
    db,
):
    """
    Create a unique test hospital and Receptionist user.
    """

    hospital_code = (
        f"AUTH-{uuid4().hex[:8].upper()}"
    )

    hospital_service = HospitalService(db)

    hospital = hospital_service.create_hospital(
        HospitalCreate(
            name="Auth Test Hospital",
            code=hospital_code,
            hospital_type=HospitalType.GENERAL,
            ownership=HospitalOwnership.PRIVATE,
            email="auth@example.com",
            phone="08000000000",
            address="1 Auth Street",
            city="Lagos",
            state="Lagos",
        )
    )

    repository = IdentityRepository(db)

    user_service = UserService(
        repository,
    )

    user = user_service.create_user(
        hospital_code=hospital.code,
        email="receptionist@example.com",
        password="password123",
        role_name="Receptionist",
    )

    repository.save()
    repository.refresh(user)

    return hospital, user


def build_auth_service(
    db,
):
    """
    Build the AuthService used by the tests.
    """

    repository = IdentityRepository(db)

    token_service = TokenService()

    service = AuthService(
        repository=repository,
        token_service=token_service,
    )

    return service, repository, token_service


def login_receptionist(
    db,
):
    """
    Create a Receptionist and authenticate them.
    """

    hospital, user = create_receptionist(
        db,
    )

    service, repository, token_service = (
        build_auth_service(db)
    )

    login_response = service.login(
        hospital_code=hospital.code,
        email="receptionist@example.com",
        password="password123",
    )

    return (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    )


# =============================================================================
# Login
# =============================================================================


def test_login_returns_access_and_refresh_tokens(
    db,
):
    """
    A valid Receptionist should receive both JWT tokens.
    """

    (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    ) = login_receptionist(db)

    assert login_response.access_token
    assert login_response.refresh_token

    access_payload = token_service.decode_token(
        login_response.access_token,
    )

    refresh_payload = token_service.decode_token(
        login_response.refresh_token,
    )

    assert (
        access_payload["sub"]
        == str(user.id)
    )

    assert (
        access_payload["hospital_id"]
        == str(hospital.id)
    )

    assert (
        access_payload["type"]
        == token_service.ACCESS_TOKEN
    )

    assert (
        "Receptionist"
        in access_payload["roles"]
    )

    assert (
        refresh_payload["sub"]
        == str(user.id)
    )

    assert (
        refresh_payload["type"]
        == token_service.REFRESH_TOKEN
    )


# =============================================================================
# Refresh
# =============================================================================


def test_refresh_token_issues_new_access_token(
    db,
):
    """
    A valid refresh token should produce a valid
    access token for the current user.
    """

    (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    ) = login_receptionist(db)

    refresh_response = service.refresh(
        refresh_token=login_response.refresh_token,
    )

    assert refresh_response.access_token

    payload = token_service.decode_token(
        refresh_response.access_token,
    )

    assert (
        payload["sub"]
        == str(user.id)
    )

    assert (
        payload["hospital_id"]
        == str(hospital.id)
    )

    assert (
        payload["type"]
        == token_service.ACCESS_TOKEN
    )

    assert (
        "Receptionist"
        in payload["roles"]
    )

    assert (
        refresh_response.refresh_token
        == login_response.refresh_token
    )


def test_access_token_cannot_be_used_as_refresh_token(
    db,
):
    """
    An access token must not be accepted as a refresh token.
    """

    (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    ) = login_receptionist(db)

    with pytest.raises(
        InvalidTokenError,
    ):
        service.refresh(
            refresh_token=login_response.access_token,
        )


def test_invalid_refresh_token_is_rejected(
    db,
):
    """
    A malformed refresh token must be rejected.
    """

    service, repository, token_service = (
        build_auth_service(db)
    )

    with pytest.raises(
        InvalidTokenError,
    ):
        service.refresh(
            refresh_token="not-a-real-token",
        )


def test_expired_refresh_token_is_rejected(
    db,
):
    """
    An expired refresh token must be rejected.
    """

    (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    ) = login_receptionist(db)

    expired_token = jwt.encode(
        {
            "sub": str(user.id),
            "type": token_service.REFRESH_TOKEN,
            "iat": 1,
            "exp": 1,
        },
        token_service.secret_key,
        algorithm=token_service.algorithm,
    )

    with pytest.raises(
        ExpiredTokenError,
    ):
        service.refresh(
            refresh_token=expired_token,
        )


# =============================================================================
# User State
# =============================================================================


def test_refresh_rejects_nonexistent_user(
    db,
):
    """
    A validly signed refresh token for a nonexistent
    user must be rejected.
    """

    service, repository, token_service = (
        build_auth_service(db)
    )

    nonexistent_user_id = str(
        uuid4()
    )

    refresh_token = (
        token_service.create_refresh_token(
            user_id=uuid4(),
        )
    )

    # Replace the subject with a nonexistent user while
    # preserving the correct signing configuration.
    refresh_token = jwt.encode(
        {
            "sub": nonexistent_user_id,
            "type": token_service.REFRESH_TOKEN,
            "iat": 1_000_000_000,
            "exp": 4_000_000_000,
        },
        token_service.secret_key,
        algorithm=token_service.algorithm,
    )

    with pytest.raises(
        InvalidTokenError,
    ):
        service.refresh(
            refresh_token=refresh_token,
        )


def test_refresh_rejects_inactive_user(
    db,
):
    """
    An inactive user must not receive a new access token
    through refresh.
    """

    (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    ) = login_receptionist(db)

    user.status = "INACTIVE"

    repository.save()
    repository.refresh(user)

    with pytest.raises(
        InactiveAccountError,
    ):
        service.refresh(
            refresh_token=login_response.refresh_token,
        )


# =============================================================================
# Role Changes
# =============================================================================


def test_refresh_uses_current_user_roles(
    db,
):
    """
    Refresh should load the user's current roles rather than
    relying on roles stored inside the refresh token.
    """

    (
        hospital,
        user,
        service,
        repository,
        token_service,
        login_response,
    ) = login_receptionist(db)

    # The refresh token contains only the user identity.
    refresh_payload = token_service.decode_token(
        login_response.refresh_token,
    )

    assert (
        "roles"
        not in refresh_payload
    )

    refresh_response = service.refresh(
        refresh_token=login_response.refresh_token,
    )

    access_payload = token_service.decode_token(
        refresh_response.access_token,
    )

    assert (
        "Receptionist"
        in access_payload["roles"]
    )

def test_refresh_token_cannot_authenticate_current_user_endpoint(db):
    """A refresh token must not be accepted as a bearer access token."""
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    _, user = create_receptionist(db)
    token_service = TokenService()

    refresh_token = token_service.create_refresh_token(
        user_id=user.id,
    )

    def override_get_db():
        yield db

    previous_get_db_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {refresh_token}",
                },
            )

        assert response.status_code == 401
    finally:
        if previous_get_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_get_db_override
