"""
==============================================================================
LIGHTBURGH EMR

Clinical Event API Tests
==============================================================================

Tests the HTTP API for Clinical Events.

Coverage
--------
• Event creation
• Missing encounter
• Missing performer
• Cross-hospital performer
• Invalid event type
• Event retrieval
• Cross-hospital event retrieval
• Encounter event listing
• Clinical occurrence ordering
• Cross-hospital event listing
==============================================================================
"""

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.context import (
    RequestContext,
    get_request_context,
)
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
# Test Helpers
# ============================================================================


def create_test_encounter(
    db,
    hospital,
    *,
    hospital_number: str,
    staff_number: str,
):
    """
    Create the Patient → Episode → Staff → Encounter chain
    required for Event API tests.
    """

    context = RequestContext(
        user_id=uuid4(),
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
            hospital_number=hospital_number,
            first_name="John",
            last_name="Doe",
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
            staff_number=staff_number,
            first_name="Jane",
            last_name="Smith",
            gender=Gender.FEMALE,
            date_of_birth=date(1992, 5, 10),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

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
        encounter_repository=EncounterRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
    )

    episode = episode_service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Clinical Event Test Episode",
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
        title="Doctor Consultation",
    )

    return context, staff, encounter


def create_test_client(
    db,
    context: RequestContext,
) -> TestClient:
    """
    Create a TestClient with the database and request context
    dependencies overridden.
    """

    def override_get_db():
        yield db

    def override_get_request_context():
        return context

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        get_request_context
    ] = override_get_request_context

    return TestClient(app)


# ============================================================================
# Create Event
# ============================================================================


def test_create_event_endpoint(
    db,
    hospital,
):
    """
    POST /api/v1/events should create a Clinical Event.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-001",
        staff_number="STF-EVT-001",
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

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["encounter_id"] == str(encounter.id)
    assert data["event_type"] == "VITALS_RECORDED"
    assert data["performed_by"] == str(staff.id)
    assert data["payload"] == {
        "temperature": 38.2,
    }


# ============================================================================
# Missing Encounter
# ============================================================================


def test_create_event_missing_encounter_returns_404(
    db,
    hospital,
):
    """
    POST /api/v1/events should return 404 for an unknown Encounter.
    """

    context, staff, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-002",
        staff_number="STF-EVT-002",
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(uuid4()),
            "event_type": "VITALS_RECORDED",
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "payload": {
                "temperature": 38.2,
            },
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Encounter not found."


# ============================================================================
# Missing Performer
# ============================================================================


def test_create_event_missing_performer_returns_404(
    db,
    hospital,
):
    """
    POST /api/v1/events should return 404 for an unknown performer.
    """

    context, _, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-003",
        staff_number="STF-EVT-003",
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter.id),
            "event_type": "VITALS_RECORDED",
            "performed_by": str(uuid4()),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "payload": {
                "temperature": 38.2,
            },
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Staff member not found."


# ============================================================================
# Cross-Hospital Performer
# ============================================================================


def test_create_event_performer_from_another_hospital_returns_403(
    db,
    hospital,
    hospital_two,
):
    """
    A Staff member belonging to another Hospital cannot perform
    an event within the current Hospital.
    """

    context_a, _, encounter_a = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-004",
        staff_number="STF-EVT-004",
    )

    _, staff_b, _ = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-EVT-005",
        staff_number="STF-EVT-005",
    )

    client = create_test_client(
        db,
        context_a,
    )

    response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter_a.id),
            "event_type": "VITALS_RECORDED",
            "performed_by": str(staff_b.id),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "payload": {
                "temperature": 37.0,
            },
        },
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "Staff member does not belong to the authenticated Hospital."
    )


# ============================================================================
# Invalid Event Type
# ============================================================================


def test_create_event_invalid_event_type_returns_422(
    db,
    hospital,
):
    """
    POST /api/v1/events should reject an invalid EventType.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-006",
        staff_number="STF-EVT-006",
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter.id),
            "event_type": "INVALID_EVENT_TYPE",
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "payload": {},
        },
    )

    assert response.status_code == 422


# ============================================================================
# Retrieve Event
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
        hospital_number="PAT-EVT-007",
        staff_number="STF-EVT-007",
    )

    client = create_test_client(
        db,
        context,
    )

    create_response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter.id),
            "event_type": "VITALS_RECORDED",
            "performed_by": str(staff.id),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
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
# Missing Event
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
        hospital_number="PAT-EVT-008",
        staff_number="STF-EVT-008",
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
# Cross-Hospital Event Retrieval
# ============================================================================


def test_get_event_from_another_hospital_returns_404(
    db,
    hospital,
    hospital_two,
):
    """
    A Hospital must not retrieve another Hospital's Clinical Event.
    """

    context_a, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-009",
        staff_number="STF-EVT-009",
    )

    context_b, staff_b, encounter_b = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-EVT-010",
        staff_number="STF-EVT-010",
    )

    client_b = create_test_client(
        db,
        context_b,
    )

    create_response = client_b.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter_b.id),
            "event_type": "CLINICAL_NOTE_RECORDED",
            "performed_by": str(staff_b.id),
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

    client_a = create_test_client(
        db,
        context_a,
    )

    response = client_a.get(
        f"/api/v1/events/{event_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Clinical Event not found."


# ============================================================================
# List Encounter Events
# ============================================================================


def test_list_encounter_events_endpoint(
    db,
    hospital,
):
    """
    GET /api/v1/events/encounters/{encounter_id} should return
    events in clinical occurrence order.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-011",
        staff_number="STF-EVT-011",
    )

    client = create_test_client(
        db,
        context,
    )

    first_time = datetime(
        2026,
        8,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )

    second_time = datetime(
        2026,
        8,
        15,
        10,
        45,
        tzinfo=timezone.utc,
    )

    second_response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter.id),
            "event_type": "VITALS_RECORDED",
            "performed_by": str(staff.id),
            "occurred_at": second_time.isoformat(),
            "payload": {
                "temperature": 38.2,
            },
        },
    )

    first_response = client.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter.id),
            "event_type": "CLINICAL_NOTE_RECORDED",
            "performed_by": str(staff.id),
            "occurred_at": first_time.isoformat(),
            "payload": {
                "note": "Patient reviewed.",
            },
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        f"/api/v1/events/encounters/{encounter.id}",
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) == 2

    assert events[0]["event_type"] == "CLINICAL_NOTE_RECORDED"
    assert events[1]["event_type"] == "VITALS_RECORDED"

    assert events[0]["occurred_at"] < events[1]["occurred_at"]


# ============================================================================
# Cross-Hospital Event Listing
# ============================================================================


def test_list_encounter_events_from_another_hospital_returns_empty_list(
    db,
    hospital,
    hospital_two,
):
    """
    A Hospital must not see another Hospital's Clinical Events.
    """

    context_a, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-012",
        staff_number="STF-EVT-012",
    )

    context_b, staff_b, encounter_b = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-EVT-013",
        staff_number="STF-EVT-013",
    )

    client_b = create_test_client(
        db,
        context_b,
    )

    create_response = client_b.post(
        "/api/v1/events",
        json={
            "encounter_id": str(encounter_b.id),
            "event_type": "CLINICAL_NOTE_RECORDED",
            "performed_by": str(staff_b.id),
            "occurred_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "payload": {
                "note": "Hospital B event.",
            },
        },
    )

    assert create_response.status_code == 201

    client_a = create_test_client(
        db,
        context_a,
    )

    response = client_a.get(
        f"/api/v1/events/encounters/{encounter_b.id}",
    )

    assert response.status_code == 200
    assert response.json() == []


# ============================================================================
# Cleanup
# ============================================================================


def teardown_function():
    """
    Clear FastAPI dependency overrides after every test.
    """

    app.dependency_overrides.clear()