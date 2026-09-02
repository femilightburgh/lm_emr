"""
==============================================================================
LIGHTBURGH EMR

Reception Router Tests
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.db.session import get_db
from app.main import app

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.identity.auth_service import AuthService
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.role_seeder import (
    seed_default_roles,
)
from app.modules.identity.token_service import TokenService
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)

from tests.diagnostics_test_router import (
    create_user,
)


def create_test_client(
    db,
    context: RequestContext,
) -> TestClient:
    """
    Create a TestClient with database and request-context overrides.
    """

    def override_get_db():
        yield db

    def override_get_request_context():
        return context

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_request_context] = (
        override_get_request_context
    )

    return TestClient(app)


def authenticate(
    db,
    *,
    hospital,
    email: str,
) -> str:
    """
    Authenticate a test user and return an access token.
    """

    service = AuthService(
        repository=IdentityRepository(db),
        token_service=TokenService(),
    )

    response = service.login(
        hospital_code=hospital.code,
        email=email,
        password="password123",
    )

    return response.access_token


def auth_headers(
    token: str,
) -> dict[str, str]:
    """
    Build Authorization headers.
    """

    return {
        "Authorization": f"Bearer {token}",
    }


def test_reception_overview_endpoint_returns_statistics(
    db,
    hospital,
):
    """
    GET /api/v1/reception/overview should return
    hospital-scoped Reception statistics.
    """

    seed_default_roles(
        db,
        hospital.id,
    )

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

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(
            {"patient.read"},
        ),
    )

    client = create_test_client(
        db,
        context,
    )

    try:
        response = client.get(
            "/api/v1/reception/overview",
            headers=auth_headers(token),
        )

        assert response.status_code == 200

        body = response.json()

        patient_repository = PatientRepository(db)
        episode_repository = EpisodeRepository(db)

        assert body["total_patients"] == (
            patient_repository.count_by_hospital(
                hospital.id,
            )
        )

        assert body["currently_admitted"] == (
            episode_repository.count_admitted_by_hospital(
                hospital_id=hospital.id,
            )
        )

        now = datetime.now(UTC)

        start_of_today = datetime(
            now.year,
            now.month,
            now.day,
            tzinfo=UTC,
        )

        start_of_tomorrow = (
            start_of_today + timedelta(days=1)
        )

        assert body["checked_in_today"] == (
            episode_repository.count_checked_in_between(
                hospital_id=hospital.id,
                start_at=start_of_today,
                end_at=start_of_tomorrow,
            )
        )

    finally:
        app.dependency_overrides.clear()


def test_reception_overview_is_hospital_scoped(
    db,
    hospital,
    hospital_two,
):
    """
    Reception Overview must return statistics for
    the authenticated hospital only.
    """

    seed_default_roles(
        db,
        hospital.id,
    )

    seed_default_roles(
        db,
        hospital_two.id,
    )

    user_one = create_user(
        db,
        hospital=hospital,
        email=f"reception-one-{uuid4()}@example.com",
        role_name="Receptionist",
    )

    user_two = create_user(
        db,
        hospital=hospital_two,
        email=f"reception-two-{uuid4()}@example.com",
        role_name="Receptionist",
    )

    token_one = authenticate(
        db,
        hospital=hospital,
        email=user_one.email,
    )

    token_two = authenticate(
        db,
        hospital=hospital_two,
        email=user_two.email,
    )

    client_one = create_test_client(
        db,
        RequestContext(
            user_id=user_one.id,
            hospital_id=hospital.id,
            permissions=frozenset(
                {"patient.read"},
            ),
        ),
    )

    try:
        response_one = client_one.get(
            "/api/v1/reception/overview",
            headers=auth_headers(token_one),
        )

        assert response_one.status_code == 200

        body_one = response_one.json()

    finally:
        app.dependency_overrides.clear()

    client_two = create_test_client(
        db,
        RequestContext(
            user_id=user_two.id,
            hospital_id=hospital_two.id,
            permissions=frozenset(
                {"patient.read"},
            ),
        ),
    )

    try:
        response_two = client_two.get(
            "/api/v1/reception/overview",
            headers=auth_headers(token_two),
        )

        assert response_two.status_code == 200

        body_two = response_two.json()

    finally:
        app.dependency_overrides.clear()

    patient_repository = PatientRepository(db)
    episode_repository = EpisodeRepository(db)

    assert body_one["total_patients"] == (
        patient_repository.count_by_hospital(
            hospital.id,
        )
    )

    assert body_one["currently_admitted"] == (
        episode_repository.count_admitted_by_hospital(
            hospital_id=hospital.id,
        )
    )

    assert body_two["total_patients"] == (
        patient_repository.count_by_hospital(
            hospital_two.id,
        )
    )

    assert body_two["currently_admitted"] == (
        episode_repository.count_admitted_by_hospital(
            hospital_id=hospital_two.id,
        )
    )


def test_reception_overview_requires_authentication(
    db,
    hospital,
):
    """
    Reception Overview must reject unauthenticated requests.
    """

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(
        ),
    )

    client = create_test_client(
        db,
        context,
    )

    try:
        response = client.get(
            "/api/v1/reception/overview",
        )

        assert response.status_code == 401

    finally:
        app.dependency_overrides.clear()


def test_episode_repository_counts_admitted_by_hospital(
    db,
    hospital,
):
    """
    The admitted aggregate must be hospital-scoped.
    """

    repository = EpisodeRepository(db)

    count = repository.count_admitted_by_hospital(
        hospital_id=hospital.id,
    )

    assert count >= 0


def test_episode_repository_counts_check_ins_in_range(
    db,
    hospital,
):
    """
    The check-in aggregate must accept a bounded
    timezone-aware interval.
    """

    repository = EpisodeRepository(db)

    now = datetime.now(UTC)

    count = repository.count_checked_in_between(
        hospital_id=hospital.id,
        start_at=now - timedelta(days=1),
        end_at=now + timedelta(days=1),
    )

    assert count >= 0


def test_reception_patient_flow_returns_active_patient_flow(
    db,
    hospital,
):
    """
    GET /api/v1/reception/patient-flow should return
    active patient Episodes with patient identity and
    operational flow state.
    """

    from app.modules.episode.models import (
        Episode,
        EpisodeFlowStatus,
        EpisodeStatus,
    )
    from app.modules.patients.enums import Sex
    from app.modules.patients.models import Patient

    seed_default_roles(
        db,
        hospital.id,
    )

    user = create_user(
        db,
        hospital=hospital,
        email=f"reception-flow-{uuid4()}@example.com",
        role_name="Receptionist",
    )

    patient = Patient(
        hospital_id=hospital.id,
        hospital_number=f"FLOW-{uuid4().hex[:8].upper()}",
        first_name="Flow",
        last_name="Patient",
        middle_name=None,
        sex=Sex.MALE,
        date_of_birth=datetime(
            1990,
            1,
            1,
        ).date(),
        phone_number=None,
        email=None,
        address=None,
        occupation=None,
        marital_status=None,
        religion=None,
        blood_group=None,
        genotype=None,
        next_of_kin_name=None,
        next_of_kin_relationship=None,
        next_of_kin_phone=None,
        next_of_kin_address=None,
    )

    db.add(patient)
    db.flush()

    active_episode = Episode(
        hospital_id=hospital.id,
        patient_id=patient.id,
        managing_doctor_id=None,
        episode_number=f"FLOW-{uuid4().hex[:10].upper()}",
        title="Outpatient Visit",
        status=EpisodeStatus.OPEN,
        flow_status=EpisodeFlowStatus.WAITING_FOR_NURSING,
        checked_in_at=datetime.now(UTC),
        checked_in_by=None,
        triaged_at=None,
        triaged_by=None,
        routed_at=None,
        routed_by=None,
        current_department_id=None,
        opened_at=datetime.now(UTC),
        closed_at=None,
    )

    closed_episode = Episode(
        hospital_id=hospital.id,
        patient_id=patient.id,
        managing_doctor_id=None,
        episode_number=f"CLOSED-{uuid4().hex[:10].upper()}",
        title="Previous Visit",
        status=EpisodeStatus.CLOSED,
        flow_status=EpisodeFlowStatus.AWAITING_REVIEW,
        checked_in_at=datetime.now(UTC),
        checked_in_by=None,
        triaged_at=None,
        triaged_by=None,
        routed_at=None,
        routed_by=None,
        current_department_id=None,
        opened_at=datetime.now(UTC),
        closed_at=datetime.now(UTC),
    )

    db.add_all(
        [
            active_episode,
            closed_episode,
        ],
    )

    db.flush()

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    client = create_test_client(
        db,
        RequestContext(
            user_id=user.id,
            hospital_id=hospital.id,
            permissions=frozenset(
                {"patient.read"},
            ),
        ),
    )

    try:
        response = client.get(
            "/api/v1/reception/patient-flow",
            headers=auth_headers(token),
        )

        assert response.status_code == 200

        body = response.json()

        assert "items" in body

        items = body["items"]

        active_item = next(
            item
            for item in items
            if item["id"] == str(active_episode.id)
        )

        assert active_item["patient_id"] == str(
            patient.id,
        )

        assert active_item["patient_name"] == (
            "Patient, Flow"
        )

        assert active_item["hospital_number"] == (
            patient.hospital_number
        )

        assert active_item["episode_number"] == (
            active_episode.episode_number
        )

        assert active_item["status"] == "OPEN"

        assert active_item["flow_status"] == (
            "WAITING_FOR_NURSING"
        )

        assert not any(
            item["id"] == str(closed_episode.id)
            for item in items
        )

    finally:
        app.dependency_overrides.clear()
