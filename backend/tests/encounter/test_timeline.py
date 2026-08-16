"""
==============================================================================
LIGHTBURGH EMR

Encounter Clinical Timeline API Tests
==============================================================================
"""

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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
from app.modules.events.enums import EventType

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
# Helpers
# ============================================================================


def create_test_encounter(
    db: Session,
    hospital,
    *,
    hospital_number: str,
    staff_number: str,
):
    """
    Create the Patient → Episode → Staff → Encounter hierarchy.
    """

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    patient_service = PatientService(
        repository=PatientRepository(db),
    )

    patient = patient_service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=hospital_number,
            first_name="Timeline",
            last_name="Patient",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=staff_number,
            first_name="Timeline",
            last_name="Clinician",
            gender=Gender.FEMALE,
            date_of_birth=date(1992, 5, 10),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

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
        title="Timeline Test Episode",
    )

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    encounter = encounter_service.create_encounter(
        context=context,
        episode_id=episode.id,
        staff_id=staff.id,
        title="Timeline Test Encounter",
    )

    return context, staff, encounter


def create_test_client(
    db: Session,
    context: RequestContext,
) -> TestClient:
    """
    Create a TestClient with database and context dependencies overridden.
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


def create_event(
    db: Session,
    context: RequestContext,
    *,
    encounter_id,
    staff_id,
    event_type: EventType,
    occurred_at: datetime,
    payload: dict,
):
    """
    Create a Clinical Event directly through ClinicalEventService.
    """

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    return service.create_event(
        context=context,
        encounter_id=encounter_id,
        event_type=event_type,
        performed_by=staff_id,
        occurred_at=occurred_at,
        payload=payload,
    )


# ============================================================================
# Empty Timeline
# ============================================================================


def test_timeline_returns_empty_list_for_encounter_without_events(
    db,
    hospital,
):
    """
    An Encounter without Clinical Events should have an empty timeline.
    """

    context, _, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-TL-001",
        staff_number="STF-TL-001",
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.get(
        f"/api/v1/encounters/{encounter.id}/timeline",
    )

    assert response.status_code == 200
    assert response.json() == []


# ============================================================================
# Timeline Ordering
# ============================================================================


def test_timeline_returns_events_in_occurrence_order(
    db,
    hospital,
):
    """
    Clinical Events should be returned chronologically by occurred_at.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-TL-002",
        staff_number="STF-TL-002",
    )

    later = datetime(
        2026,
        8,
        15,
        11,
        0,
        tzinfo=timezone.utc,
    )

    earlier = datetime(
        2026,
        8,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )

    create_event(
        db,
        context,
        encounter_id=encounter.id,
        staff_id=staff.id,
        event_type=EventType.VITALS_RECORDED,
        occurred_at=later,
        payload={
            "temperature": 38.2,
        },
    )

    create_event(
        db,
        context,
        encounter_id=encounter.id,
        staff_id=staff.id,
        event_type=EventType.CLINICAL_NOTE_RECORDED,
        occurred_at=earlier,
        payload={
            "note": "Patient reviewed.",
        },
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.get(
        f"/api/v1/encounters/{encounter.id}/timeline",
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) == 2

    assert events[0]["event_type"] == "CLINICAL_NOTE_RECORDED"
    assert events[1]["event_type"] == "VITALS_RECORDED"

    assert events[0]["occurred_at"] < events[1]["occurred_at"]


# ============================================================================
# Mixed Clinical Timeline
# ============================================================================


def test_timeline_combines_different_clinical_event_types(
    db,
    hospital,
):
    """
    Different Clinical Event types should appear in one timeline.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-TL-003",
        staff_number="STF-TL-003",
    )

    create_event(
        db,
        context,
        encounter_id=encounter.id,
        staff_id=staff.id,
        event_type=EventType.VITALS_RECORDED,
        occurred_at=datetime(
            2026,
            8,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        payload={
            "temperature": 38.2,
            "heart_rate": 104,
        },
    )

    create_event(
        db,
        context,
        encounter_id=encounter.id,
        staff_id=staff.id,
        event_type=EventType.CLINICAL_NOTE_RECORDED,
        occurred_at=datetime(
            2026,
            8,
            15,
            10,
            45,
            tzinfo=timezone.utc,
        ),
        payload={
            "note": "Patient reviewed.",
        },
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.get(
        f"/api/v1/encounters/{encounter.id}/timeline",
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) == 2

    assert events[0]["event_type"] == "VITALS_RECORDED"
    assert events[1]["event_type"] == "CLINICAL_NOTE_RECORDED"


# ============================================================================
# Missing Encounter
# ============================================================================


def test_timeline_returns_404_for_missing_encounter(
    db,
    hospital,
):
    """
    Timeline retrieval should return 404 for an unknown Encounter.
    """

    context, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-TL-004",
        staff_number="STF-TL-004",
    )

    client = create_test_client(
        db,
        context,
    )

    response = client.get(
        f"/api/v1/encounters/{uuid4()}/timeline",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Encounter not found."


# ============================================================================
# Hospital Tenancy
# ============================================================================


def test_timeline_cannot_access_another_hospital_encounter(
    db,
    hospital,
    hospital_two,
):
    """
    A Hospital must not retrieve another Hospital's timeline.
    """

    context_a, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-TL-005",
        staff_number="STF-TL-005",
    )

    context_b, staff_b, encounter_b = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-TL-006",
        staff_number="STF-TL-006",
    )

    create_event(
        db,
        context_b,
        encounter_id=encounter_b.id,
        staff_id=staff_b.id,
        event_type=EventType.VITALS_RECORDED,
        occurred_at=datetime(
            2026,
            8,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        payload={
            "temperature": 37.5,
        },
    )

    client_a = create_test_client(
        db,
        context_a,
    )

    response = client_a.get(
        f"/api/v1/encounters/{encounter_b.id}/timeline",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Encounter not found."


# ============================================================================
# Cleanup
# ============================================================================


def teardown_function():
    """
    Clear FastAPI dependency overrides after every test.
    """

    app.dependency_overrides.clear()