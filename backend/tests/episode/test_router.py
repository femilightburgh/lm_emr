"""
==============================================================================
LIGHTBURGH EMR

Episode API Router Tests

==============================================================================

Tests the HTTP API exposed by the Episode module.

==============================================================================
"""

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.db.session import get_db
from app.main import app

from app.modules.episode.models import EpisodeFlowStatus

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import (
    EpisodeService,
)

from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)
from app.modules.patients.services.patient_service import (
    PatientService,
)

from app.modules.staff.enums import (
    EmploymentStatus,
    EmploymentType,
    Gender,
    Profession,
)
from app.modules.staff.employment_repository import (
    StaffEmploymentRepository,
)
from app.modules.staff.repository import (
    StaffRepository,
)
from app.modules.staff.schemas import (
    StaffCreate,
)
from app.modules.staff.service import (
    StaffService,
)
from app.modules.organization.repository import HospitalRepository

from tests.helpers.episode import build_episode_service


# ============================================================================
# Helpers
# ============================================================================


def create_patient(
    db: Session,
    hospital,
):
    """
    Create a test patient.
    """

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = PatientService(
        repository=PatientRepository(db),
    )

    return service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=f"EP-{uuid4().hex[:12]}",
            first_name="Test",
            last_name="Patient",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )


def create_authenticated_staff(
    db: Session,
    hospital,
):
    """
    Create a UserAccount and Staff profile linked to that account.

    Returns
    -------
    tuple
        (user, staff, context)
    """

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"episode-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"EP-STF-{uuid4().hex[:10]}",
            first_name="Reception",
            last_name="Staff",
            gender=Gender.FEMALE,
            date_of_birth=date(1990, 1, 1),
            profession=Profession.ADMINISTRATOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff.user_account_id = user.id

    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    return user, staff, context


def create_episode(
    db: Session,
    hospital,
    context: RequestContext,
):
    """
    Create a test Episode.
    """

    patient = create_patient(
        db=db,
        hospital=hospital,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    return episode


# ============================================================================
# Test Client
# ============================================================================


@pytest.fixture
def client(
    db: Session,
    hospital,
):
    """
    Provide a TestClient with database and request-context dependencies
    overridden for the test database.
    """

    def override_get_db():
        yield db

    def override_get_request_context():
        return RequestContext(
            user_id=uuid4(),
            hospital_id=hospital.id,
            permissions=frozenset(),
        )

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_request_context] = (
        override_get_request_context
    )

    yield TestClient(app)

    app.dependency_overrides.clear()


# ============================================================================
# Check-In
# ============================================================================


def test_check_in_episode_endpoint(
    db,
    hospital,
):
    """
    A valid authenticated Staff member can check in an Episode.
    """

    user, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    episode = create_episode(
        db=db,
        hospital=hospital,
        context=context,
    )

    def override_get_db():
        yield db

    def override_get_request_context():
        return context

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_request_context] = (
        override_get_request_context
    )

    try:
        client = TestClient(app)

        response = client.post(
            f"/api/v1/episodes/{episode.id}/check-in",
        )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(episode.id)

    assert (
        body["flow_status"]
        == EpisodeFlowStatus.WAITING_FOR_NURSING.value
    )

    assert body["checked_in_by"] == str(staff.id)

    assert body["checked_in_by"] != str(user.id)

    assert body["checked_in_at"] is not None


def test_check_in_episode_endpoint_rejects_second_check_in(
    db,
    hospital,
):
    """
    An Episode cannot be checked in twice.
    """

    _, _, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    episode = create_episode(
        db=db,
        hospital=hospital,
        context=context,
    )

    def override_get_db():
        yield db

    def override_get_request_context():
        return context

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_request_context] = (
        override_get_request_context
    )

    try:
        client = TestClient(app)

        first_response = client.post(
            f"/api/v1/episodes/{episode.id}/check-in",
        )

        second_response = client.post(
            f"/api/v1/episodes/{episode.id}/check-in",
        )

    finally:
        app.dependency_overrides.clear()

    assert first_response.status_code == 200

    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "Episode is not awaiting check-in."
    )
