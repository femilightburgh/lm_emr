"""
==============================================================================
LIGHTBURGH EMR

Clinical Event Service Tests
==============================================================================

Purpose
-------
Tests the business logic for Clinical Events.

Clinical hierarchy
------------------
Patient
    ↓
Episode
    ↓
Encounter
    ↓
Clinical Event

Coverage
--------
• Event creation
• Encounter ownership
• Hospital tenancy
• Event performer validation
• Event timing
• Event type validation

==============================================================================
"""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from app.core.context import RequestContext

from app.modules.events.enums import EventType
from app.modules.events.exceptions import (
    EncounterNotFoundError,
    EventNotFoundError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService

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
    required for Event tests.
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
        title="Medical Consultation",
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


# ============================================================================
# Create Event
# ============================================================================


def test_create_event_creates_event(
    db,
    hospital,
):
    """
    A valid clinical event should be created for an encounter.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-001",
        staff_number="STF-EVT-001",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    occurred_at = datetime.now(timezone.utc)

    event = service.create_event(
        context=context,
        encounter_id=encounter.id,
        event_type=EventType.VITALS_RECORDED,
        performed_by=staff.id,
        occurred_at=occurred_at,
        payload={
            "temperature": 38.2,
        },
    )

    assert event.id is not None
    assert event.encounter_id == encounter.id
    assert event.event_type == EventType.VITALS_RECORDED
    assert event.performed_by == staff.id
    assert event.occurred_at == occurred_at
    assert event.payload == {
        "temperature": 38.2,
    }


# ============================================================================
# Hospital Tenancy
# ============================================================================


def test_event_rejects_encounter_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital cannot create an event against another hospital's encounter.
    """

    context_a, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-002",
        staff_number="STF-EVT-002",
    )

    _, staff_b, encounter_b = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-EVT-003",
        staff_number="STF-EVT-003",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    with pytest.raises(EncounterNotFoundError):
        service.create_event(
            context=context_a,
            encounter_id=encounter_b.id,
            event_type=EventType.VITALS_RECORDED,
            performed_by=staff_b.id,
            occurred_at=datetime.now(timezone.utc),
            payload={
                "temperature": 37.0,
            },
        )


def test_event_rejects_performer_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital professional from another hospital cannot perform an event
    within the current hospital's encounter.
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

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    with pytest.raises(StaffHospitalMismatchError):
        service.create_event(
            context=context_a,
            encounter_id=encounter_a.id,
            event_type=EventType.VITALS_RECORDED,
            performed_by=staff_b.id,
            occurred_at=datetime.now(timezone.utc),
            payload={
                "temperature": 37.0,
            },
        )


# ============================================================================
# Validation
# ============================================================================


def test_event_rejects_missing_encounter(
    db,
    hospital,
):
    """
    An event cannot be created without a valid encounter.
    """

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    # Create a valid staff member so that the test specifically
    # exercises encounter validation.
    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-EVT-006",
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

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    with pytest.raises(EncounterNotFoundError):
        service.create_event(
            context=context,
            encounter_id=uuid4(),
            event_type=EventType.VITALS_RECORDED,
            performed_by=staff.id,
            occurred_at=datetime.now(timezone.utc),
            payload={
                "temperature": 37.0,
            },
        )


def test_event_rejects_missing_performer(
    db,
    hospital,
):
    """
    An event cannot be created by a staff member who does not exist.
    """

    context, _, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-007",
        staff_number="STF-EVT-007",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    with pytest.raises(StaffNotFoundError):
        service.create_event(
            context=context,
            encounter_id=encounter.id,
            event_type=EventType.VITALS_RECORDED,
            performed_by=uuid4(),
            occurred_at=datetime.now(timezone.utc),
            payload={
                "temperature": 37.0,
            },
        )


def test_event_rejects_invalid_event_type(
    db,
    hospital,
):
    """
    An event must have a valid event type.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-008",
        staff_number="STF-EVT-008",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    with pytest.raises(ValueError):
        service.create_event(
            context=context,
            encounter_id=encounter.id,
            event_type="INVALID_EVENT_TYPE",
            performed_by=staff.id,
            occurred_at=datetime.now(timezone.utc),
            payload={
                "temperature": 37.0,
            },
        )


# ============================================================================
# Timing
# ============================================================================


def test_event_preserves_clinical_occurrence_time(
    db,
    hospital,
):
    """
    The time the clinical action occurred must be preserved independently
    from the database creation time.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVT-009",
        staff_number="STF-EVT-009",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    occurred_at = datetime(
        2026,
        8,
        10,
        14,
        30,
        tzinfo=timezone.utc,
    )

    event = service.create_event(
        context=context,
        encounter_id=encounter.id,
        event_type=EventType.WOUND_DRESSED,
        performed_by=staff.id,
        occurred_at=occurred_at,
        payload={
            "site": "left foot",
        },
    )

    assert event.occurred_at == occurred_at
    assert event.created_at is not None
    assert event.occurred_at != event.created_at


# ============================================================================
# Retrieve Event
# ============================================================================


def test_get_event_returns_event(
    db,
    hospital,
):
    """
    A hospital should be able to retrieve its own Clinical Event.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVENT-GET-001",
        staff_number="STF-EVENT-GET-001",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    event = service.create_event(
        context=context,
        encounter_id=encounter.id,
        event_type=EventType.VITALS_RECORDED,
        performed_by=staff.id,
        occurred_at=datetime.now(timezone.utc),
        payload={
            "temperature": 37.2,
        },
    )

    retrieved = service.get_event(
        context=context,
        event_id=event.id,
    )

    assert retrieved.id == event.id
    assert retrieved.encounter_id == encounter.id


def test_get_event_rejects_event_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital must not retrieve another hospital's Clinical Event.
    """

    context_one, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVL-H1-01",
        staff_number="STF-EVL-H1-01",
    )

    context_two, staff_two, encounter_two = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-EVL-H2-01",
        staff_number="STF-EVL-H2-01",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    event = service.create_event(
        context=context_two,
        encounter_id=encounter_two.id,
        event_type=EventType.VITALS_RECORDED,
        performed_by=staff_two.id,
        occurred_at=datetime.now(timezone.utc),
        payload={
            "temperature": 37.5,
        },
    )

    with pytest.raises(EventNotFoundError):
        service.get_event(
            context=context_one,
            event_id=event.id,
        )


def test_get_event_rejects_missing_event(
    db,
    hospital,
):
    """
    Retrieving a nonexistent Clinical Event should fail.
    """

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    with pytest.raises(EventNotFoundError):
        service.get_event(
            context=context,
            event_id=uuid4(),
        )


# ============================================================================
# List Encounter Events
# ============================================================================


def test_list_encounter_events_returns_events_in_occurrence_order(
    db,
    hospital,
):
    """
    Encounter Events should be returned in clinical occurrence order.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVENT-LIST-001",
        staff_number="STF-EVENT-LIST-001",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    first_time = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    second_time = datetime(
        2026,
        1,
        1,
        10,
        30,
        tzinfo=timezone.utc,
    )

    first = service.create_event(
        context=context,
        encounter_id=encounter.id,
        event_type=EventType.VITALS_RECORDED,
        performed_by=staff.id,
        occurred_at=second_time,
        payload={
            "temperature": 37.2,
        },
    )

    second = service.create_event(
        context=context,
        encounter_id=encounter.id,
        event_type=EventType.CLINICAL_NOTE_RECORDED,
        performed_by=staff.id,
        occurred_at=first_time,
        payload={
            "note": "Patient reviewed.",
        },
    )

    events = service.list_encounter_events(
        context=context,
        encounter_id=encounter.id,
    )

    assert [event.id for event in events] == [
        second.id,
        first.id,
    ]


def test_list_encounter_events_does_not_return_another_hospital_events(
    db,
    hospital,
    hospital_two,
):
    """
    Encounter event listing must respect hospital tenancy.
    """

    context_one, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-EVL-H1-01",
        staff_number="STF-EVL-H1-01",
    )

    context_two, staff_two, encounter_two = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-EVL-H2-01",
        staff_number="STF-EVL-H2-01",
    )

    service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    service.create_event(
        context=context_two,
        encounter_id=encounter_two.id,
        event_type=EventType.VITALS_RECORDED,
        performed_by=staff_two.id,
        occurred_at=datetime.now(timezone.utc),
        payload={
            "temperature": 37.8,
        },
    )

    events = service.list_encounter_events(
        context=context_one,
        encounter_id=encounter_two.id,
    )

    assert events == []