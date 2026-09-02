"""
==============================================================================
LIGHTBURGH EMR

Vitals Router Tests
==============================================================================

Tests the HTTP API for recording patient vital signs.

Coverage
--------
• Successful vitals recording
• Partial vitals recording
• Missing encounter
• Missing performer
• Performer from another hospital
• Invalid clinical measurements
• Missing all measurements
==============================================================================
"""

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.context import RequestContext, get_request_context
from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount
from app.db.session import get_db
from app.main import app

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.repositories.episode_disposition_repository import (
    EpisodeDispositionRepository,
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

from app.modules.organization.repository import HospitalRepository

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)
from app.modules.patients.services.patient_service import (
    PatientService,
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


# ============================================================================
# Test Data Helper
# ============================================================================


def create_test_encounter(
    db,
    hospital,
    *,
    hospital_number: str | None = None,
    staff_number: str | None = None,
):
    """
    Create the minimum valid Patient → Episode → Staff → Encounter
    hierarchy required by the Vitals API.
    """

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"vitals-api-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    # ------------------------------------------------------------------
    # Patient
    # ------------------------------------------------------------------

    patient_service = PatientService(
        repository=PatientRepository(db),
    )

    patient = patient_service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=hospital_number or f"PAT-{uuid4().hex[:8]}",
            first_name="Vitals",
            last_name="Patient",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )

    # ------------------------------------------------------------------
    # Staff
    # ------------------------------------------------------------------

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=staff_number or f"STF-EVENT-{uuid4().hex[:8]}",
            first_name="Vitals",
            last_name="Clinician",
            gender=Gender.MALE,
            date_of_birth=date(1985, 1, 1),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff.user_account_id = user.id
    db.flush()

    # ------------------------------------------------------------------
    # Episode
    # ------------------------------------------------------------------

    episode_repository = EpisodeRepository(db)

    episode_service = EpisodeService(
        repository=episode_repository,
        patient_repository=PatientRepository(db),
        number_generator=EpisodeNumberGenerator(
            repository=episode_repository,
        ),
        encounter_service=EncounterService(
            repository=EncounterRepository(db),
            episode_repository=episode_repository,
            staff_repository=StaffRepository(
                session=db,
            ),
        ),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
        disposition_repository=EpisodeDispositionRepository(db),
    )

    episode = episode_service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Vitals Test Episode",
    )

    # ------------------------------------------------------------------
    # Encounter
    # ------------------------------------------------------------------

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    encounter = encounter_service.create_encounter(
        context=context,
        episode_id=episode.id,
        staff_id=staff.id,
        title="Vitals Test Encounter",
    )

    return context, staff, encounter


# ============================================================================
# Test Client
# ============================================================================


def create_test_client(
    db,
    context,
):
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


# ============================================================================
# Successful Recording
# ============================================================================


def test_record_vitals_endpoint(
    db,
    hospital,
):
    """
    POST /api/v1/vitals should record a complete set of vital signs.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    client = create_test_client(
        db,
        context,
    )

    occurred_at = datetime(
        2026,
        8,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(encounter.id),
            "performed_by": str(staff.id),
            "occurred_at": occurred_at.isoformat(),
            "temperature": 38.2,
            "heart_rate": 104,
            "respiratory_rate": 22,
            "systolic_bp": 145,
            "diastolic_bp": 92,
            "spo2": 96,
            "weight": 72.5,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["encounter_id"] == str(encounter.id)
    assert data["event_type"] == "VITALS_RECORDED"
    assert data["performed_by"] == str(staff.id)

    assert datetime.fromisoformat(
        data["occurred_at"].replace("Z", "+00:00")
    ) == occurred_at

    assert data["payload"] == {
        "temperature": 38.2,
        "heart_rate": 104,
        "respiratory_rate": 22,
        "systolic_bp": 145,
        "diastolic_bp": 92,
        "spo2": 96,
        "weight": 72.5,
    }


# ============================================================================
# Partial Vitals
# ============================================================================


def test_record_partial_vitals_endpoint(
    db,
    hospital,
):
    """
    The API should permit recording only the measurements that are available.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(encounter.id),
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "temperature": 38.4,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_type"] == "VITALS_RECORDED"
    assert data["payload"] == {
        "temperature": 38.4,
    }


# ============================================================================
# Missing Encounter
# ============================================================================


def test_record_vitals_missing_encounter_returns_404(
    db,
    hospital,
):
    """
    A nonexistent encounter should produce HTTP 404.
    """

    context, staff, _ = create_test_encounter(
        db,
        hospital,
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(uuid4()),
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "temperature": 37.2,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Encounter not found."


# ============================================================================
# Missing Performer
# ============================================================================


def test_record_vitals_authenticated_user_without_staff_returns_404(
    db,
    hospital,
):
    """
    An authenticated UserAccount without a Staff profile cannot record vitals.
    """

    from app.modules.identity.enums import AccountStatus
    from app.modules.identity.models import UserAccount

    context, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"no-staff-api-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(encounter.id),
            "performed_by": str(uuid4()),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "temperature": 37.2,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Staff member not found."


def test_record_vitals_authenticated_user_from_another_hospital_returns_404(
    db,
    hospital,
    hospital_two,
):
    """
    An authenticated user whose Staff profile belongs to another
    hospital is not a Staff member of the authenticated hospital.
    """

    from app.modules.identity.enums import AccountStatus
    from app.modules.identity.models import UserAccount

    context, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    user = UserAccount(
        hospital_id=hospital_two.id,
        email=f"foreign-api-{uuid4()}@example.com",
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

    foreign_staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital_two.id,
            staff_number=f"STF-VITALS-FOREIGN-{uuid4().hex[:8]}",
            first_name="Foreign",
            last_name="Hospital",
            gender=Gender.MALE,
            date_of_birth=date(1985, 1, 1),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    foreign_staff.user_account_id = user.id
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(encounter.id),
            "performed_by": str(foreign_staff.id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "temperature": 37.2,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Staff member not found."


def test_record_vitals_invalid_measurement_returns_422(
    db,
    hospital,
):
    """
    Structurally invalid measurements should be rejected by Pydantic.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(encounter.id),
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "heart_rate": -5,
        },
    )

    assert response.status_code == 422


# ============================================================================
# No Measurements
# ============================================================================


def test_record_vitals_without_measurements_returns_422(
    db,
    hospital,
):
    """
    The request must contain at least one vital measurement.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/vitals",
        json={
            "encounter_id": str(encounter.id),
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 422


# ============================================================================
# Retrieve Clinical Event
# ============================================================================


def test_get_event_endpoint(
    db,
    hospital,
):
    """
    GET /api/v1/events/{event_id} should return an existing event.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number=f"PAT-EV-GET-{uuid4().hex[:8]}",
        staff_number=f"STF-EV-GET-{uuid4().hex[:8]}",
    )

    client = create_test_client(
        db,
        context,
    )

    occurred_at = datetime(
        2026,
        8,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )

    create_response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter.id),
            "event_type": "VITALS_RECORDED",
            "performed_by": str(staff.id),
            "occurred_at": occurred_at.isoformat(),
            "payload": {
                "temperature": 38.2,
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/events/{event_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == event_id
    assert data["encounter_id"] == str(encounter.id)
    assert data["event_type"] == "VITALS_RECORDED"
    assert data["performed_by"] == str(staff.id)
    assert data["payload"] == {
        "temperature": 38.2,
    }


# ============================================================================
# Missing Clinical Event
# ============================================================================


def test_get_event_missing_event_returns_404(
    db,
    hospital,
):
    """
    GET /api/v1/events/{event_id} should return 404 for an unknown event.
    """

    context, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number=f"PAT-MISS-{uuid4().hex[:6]}",
        staff_number=f"STF-MISS-{uuid4().hex[:6]}",
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.get(
        f"/api/v1/events/{uuid4()}",
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Clinical Event not found."


# ============================================================================
# Cross-Hospital Clinical Event
# ============================================================================


def test_get_event_from_another_hospital_returns_404(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital must not retrieve another hospital's Clinical Event.
    """

    context_one, staff_one, encounter_one = create_test_encounter(
        db,
        hospital,
        hospital_number=f"PAT-EV-H1-{uuid4().hex[:8]}",
        staff_number=f"STF-EV-H1-{uuid4().hex[:8]}",
    )

    context_two, staff_two, encounter_two = create_test_encounter(
        db,
        hospital_two,
        hospital_number=f"PAT-EV-H2-{uuid4().hex[:8]}",
        staff_number=f"STF-EV-H2-{uuid4().hex[:8]}",
    )

    # ------------------------------------------------------------------
    # Create Event in Hospital B
    # ------------------------------------------------------------------

    client_two = create_test_client(
        db,
        context_two,
    )

    create_response = client_two.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter_two.id),
            "event_type": "CLINICAL_NOTE_RECORDED",
            "performed_by": str(staff_two.id),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "payload": {
                "note": "Hospital B event.",
            },
        },
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    # ------------------------------------------------------------------
    # Hospital A attempts to retrieve Hospital B's event
    # ------------------------------------------------------------------

    client_one = create_test_client(
        db,
        context_one,
    )

    response = client_one.get(
        f"/api/v1/events/{event_id}",
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Clinical Event not found."


# ============================================================================
# Cleanup
# ============================================================================


def teardown_function():
    """
    Clear FastAPI dependency overrides after every test.
    """

    app.dependency_overrides.clear()