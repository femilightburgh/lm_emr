"""
==============================================================================
LIGHTBURGH EMR

Episode Service Tests
==============================================================================

Purpose
-------
Tests the business logic for Episodes of Care.

Coverage
--------
• Episode creation
• Episode retrieval
• Episode admission
• Episode lifecycle
• Hospital/tenant isolation
• Episode numbering
• Invalid lifecycle transitions
• Admission/Encounter validation
• Admission Clinical Event creation
• Admission transaction atomicity
==============================================================================
"""

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from app.core.context import RequestContext

from app.modules.episode.exceptions import (
    EncounterNotBelongingToEpisodeError,
    EncounterNotOpenError,
    EpisodeAlreadyAdmittedError,
    EpisodeAlreadyCancelledError,
    EpisodeAlreadyClosedError,
    EpisodeNotAwaitingCheckInError,
    EpisodeNotFoundError,
    PatientNotFoundError,
    StaffNotFoundError,
)

from app.modules.episode.models import (
    EpisodeFlowStatus,
    EpisodeStatus,
)

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)

from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)

from app.modules.patients.services.patient_service import (
    PatientService,
)

from app.modules.encounter.exceptions import (
    EncounterNotFoundError,
)

from app.modules.encounter.models import (
    Encounter,
    EncounterStatus,
)

from app.modules.events.enums import EventType

from app.modules.events.repositories import (
    ClinicalEventRepository,
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

from app.modules.organization.repository import HospitalRepository

from tests.helpers.episode import build_episode_service
from app.modules.identity.models import UserAccount
from app.modules.identity.enums import AccountStatus


# =============================================================================
# Helpers
# =============================================================================


def build_context(hospital_id):
    """
    Build a RequestContext for a hospital.
    """

    return RequestContext(
        user_id=uuid4(),
        hospital_id=hospital_id,
        permissions=frozenset(),
    )


def create_patient(
    db,
    hospital_id,
    hospital_number="PAT-001",
):
    """
    Create a patient belonging to the specified Hospital.
    """

    context = build_context(hospital_id)

    patient_service = PatientService(
        repository=PatientRepository(db),
    )

    return patient_service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital_id,
            hospital_number=hospital_number,
            first_name="John",
            last_name="Doe",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )


def create_staff(
    db,
    hospital,
    staff_number="STF-001",
):
    """
    Create a Staff member belonging to the supplied Hospital.

    StaffService owns Staff validation and persistence.
    """

    staff_service = StaffService(
        repository=StaffRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    staff = staff_service.create_staff(
        data=StaffCreate(
            hospital_id=hospital.id,
            staff_number=staff_number,
            first_name="John",
            last_name="Doctor",
            gender=Gender.MALE,
            profession=Profession.DOCTOR,
            date_of_birth=date(1990, 1, 1),
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date.today(),
        ),
    )

    return staff

def create_authenticated_staff(
    db,
    hospital,
):
    """
    Create a Staff member linked to a real UserAccount.

    This helper is used for tests that need to represent
    an authenticated Staff member.
    """

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"staff-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    staff = create_staff(
        db=db,
        hospital=hospital,
    )

    staff.user_account_id = user.id

    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    return user, staff, context


def create_open_encounter(
    db,
    hospital,
    episode,
    staff,
):
    """
    Create an OPEN Encounter belonging to the supplied Episode.

    The Encounter represents the professional interaction through
    which an admission action may be performed.
    """

    encounter = Encounter(
        episode_id=episode.id,
        staff_id=staff.id,
        title="Admission Assessment",
        status=EncounterStatus.OPEN,
        started_at=datetime.now(UTC),
        ended_at=None,
    )

    db.add(encounter)
    db.commit()
    db.refresh(encounter)

    return encounter


def create_episode_with_encounter(
    db,
    hospital,
    *,
    hospital_number="PAT-ADM-001",
    staff_number="STF-ADM-001",
):
    """
    Create the clinical context required to admit an Episode.

    Creates:

        Patient
            ↓
        OPEN Episode
            ↓
        OPEN Encounter

    The Encounter represents the professional interaction through
    which the admission action is performed.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number=hospital_number,
    )

    staff = create_staff(
        db=db,
        hospital=hospital,
        staff_number=staff_number,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    encounter = create_open_encounter(
        db=db,
        hospital=hospital,
        episode=episode,
        staff=staff,
    )

    return (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    )


# =============================================================================
# Create
# =============================================================================


def test_create_episode_creates_open_episode(
    db,
    hospital,
):
    """
    A valid Episode should be created with OPEN status.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    assert episode.id is not None
    assert episode.hospital_id == hospital.id
    assert episode.patient_id == patient.id
    assert episode.title == "Medical Consultation"
    assert episode.status == EpisodeStatus.OPEN
    assert episode.opened_at is not None
    assert episode.closed_at is None


def test_create_episode_generates_episode_number(
    db,
    hospital,
):
    """
    Episode numbers should be generated automatically.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    assert episode.episode_number is not None
    assert episode.episode_number.startswith("EPI-")


def test_create_episode_increments_episode_number(
    db,
    hospital,
):
    """
    Each newly created Episode should receive the next Episode number.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    first_episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="First Consultation",
    )

    second_episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Second Consultation",
    )

    assert first_episode.episode_number == "EPI-00000001"
    assert second_episode.episode_number == "EPI-00000002"


def test_create_episode_rejects_patient_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital must not be able to create an Episode for another
    hospital's patient.
    """

    patient = create_patient(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="PAT-002",
    )

    context = build_context(hospital.id)

    service = build_episode_service(db)

    with pytest.raises(PatientNotFoundError):
        service.create_episode(
            context=context,
            patient_id=patient.id,
            title="Unauthorized Consultation",
        )


def test_create_episode_rejects_missing_patient(
    db,
    hospital,
):
    """
    Creating an Episode for a nonexistent patient should fail.
    """

    context = build_context(hospital.id)

    service = build_episode_service(db)

    with pytest.raises(PatientNotFoundError):
        service.create_episode(
            context=context,
            patient_id=uuid4(),
            title="Medical Consultation",
        )


# =============================================================================
# Retrieve
# =============================================================================


def test_get_episode_returns_episode_for_same_hospital(
    db,
    hospital,
):
    """
    A hospital should be able to retrieve its own Episode.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    created = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    retrieved = service.get_episode(
        context=context,
        episode_id=created.id,
    )

    assert retrieved.id == created.id
    assert retrieved.hospital_id == hospital.id


def test_get_episode_rejects_episode_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital should not be able to retrieve another hospital's Episode.
    """

    patient = create_patient(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="PAT-003",
    )

    hospital_two_context = build_context(hospital_two.id)

    service = build_episode_service(db)

    episode = service.create_episode(
        context=hospital_two_context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    hospital_one_context = build_context(hospital.id)

    with pytest.raises(EpisodeNotFoundError):
        service.get_episode(
            context=hospital_one_context,
            episode_id=episode.id,
        )


def test_get_episode_rejects_missing_episode(
    db,
    hospital,
):
    """
    Retrieving a nonexistent Episode should fail.
    """

    context = build_context(hospital.id)

    service = build_episode_service(db)

    with pytest.raises(EpisodeNotFoundError):
        service.get_episode(
            context=context,
            episode_id=uuid4(),
        )


# =============================================================================
# Admission
# =============================================================================


def test_admit_episode_changes_open_to_admitted(
    db,
    hospital,
):
    """
    An OPEN Episode should transition to ADMITTED through an
    OPEN Encounter.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    admitted = service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
    )

    assert admitted.status == EpisodeStatus.ADMITTED
    assert admitted.closed_at is None


def test_admit_episode_keeps_encounter_open(
    db,
    hospital,
):
    """
    Admitting an Episode must not close the Encounter through which
    the admission was performed.

    The Episode transitions to ADMITTED while the Encounter remains
    OPEN so that the professional interaction can continue.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    admitted = service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
    )

    db.refresh(encounter)

    assert admitted.status == EpisodeStatus.ADMITTED
    assert encounter.status == EncounterStatus.OPEN
    assert encounter.ended_at is None


def test_admit_episode_creates_admission_event(
    db,
    hospital,
):
    """
    Admission should create exactly one EPISODE_ADMITTED event.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
    )

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type == EventType.EPISODE_ADMITTED
    assert event.encounter_id == encounter.id
    assert event.performed_by == staff.id
    assert event.payload["episode_id"] == str(
        episode.id,
    )


def test_admit_episode_rejects_already_admitted_episode(
    db,
    hospital,
):
    """
    An ADMITTED Episode cannot be admitted again.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
    )

    with pytest.raises(EpisodeAlreadyAdmittedError):
        service.admit_episode(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
        )


def test_admit_episode_rejects_closed_episode(
    db,
    hospital,
):
    """
    A CLOSED Episode cannot be admitted.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyClosedError):
        service.admit_episode(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
        )


def test_admit_episode_rejects_cancelled_episode(
    db,
    hospital,
):
    """
    A CANCELLED Episode cannot be admitted.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    service.cancel_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyCancelledError):
        service.admit_episode(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
        )


def test_admit_episode_rejects_encounter_from_another_episode(
    db,
    hospital,
):
    """
    An Encounter from another Episode cannot be used to admit
    the current Episode.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-ADM-002",
    )

    staff = create_staff(
        db=db,
        hospital=hospital,
        staff_number="STF-ADM-002",
    )

    service = build_episode_service(db)

    episode_one = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Episode One",
    )

    episode_two = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Episode Two",
    )

    encounter_two = create_open_encounter(
        db=db,
        hospital=hospital,
        episode=episode_two,
        staff=staff,
    )

    with pytest.raises(EncounterNotBelongingToEpisodeError):
        service.admit_episode(
            context=context,
            episode_id=episode_one.id,
            encounter_id=encounter_two.id,
        )


def test_admit_episode_rejects_closed_encounter(
    db,
    hospital,
):
    """
    Admission cannot be performed through a CLOSED Encounter.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    encounter.status = EncounterStatus.CLOSED
    encounter.ended_at = datetime.now(UTC)

    db.commit()
    db.refresh(encounter)

    with pytest.raises(EncounterNotOpenError):
        service.admit_episode(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
        )


def test_admit_episode_rejects_missing_encounter(
    db,
    hospital,
):
    """
    Admission requires an existing Encounter.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-ADM-003",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    with pytest.raises(EncounterNotFoundError):
        service.admit_episode(
            context=context,
            episode_id=episode.id,
            encounter_id=uuid4(),
        )


def test_admit_episode_rolls_back_if_event_creation_fails(
    db,
    hospital,
    monkeypatch,
):
    """
    Admission and its Clinical Event must succeed or fail together.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    def fail_create_event(*args, **kwargs):
        raise RuntimeError(
            "Event creation failed",
        )

    monkeypatch.setattr(
        service.event_service,
        "create_event",
        fail_create_event,
    )

    with pytest.raises(RuntimeError):
        service.admit_episode(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
        )

    db.refresh(episode)

    assert episode.status == EpisodeStatus.OPEN

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert events == []


# =============================================================================
# Close
# =============================================================================


def test_close_episode_closes_open_episode(
    db,
    hospital,
):
    """
    An OPEN Episode should transition to CLOSED.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    closed = service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    assert closed.status == EpisodeStatus.CLOSED
    assert closed.closed_at is not None


def test_close_episode_closes_admitted_episode(
    db,
    hospital,
):
    """
    An ADMITTED Episode should transition to CLOSED.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
    )

    closed = service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    assert closed.status == EpisodeStatus.CLOSED
    assert closed.closed_at is not None


def test_close_episode_rejects_already_closed_episode(
    db,
    hospital,
):
    """
    A CLOSED Episode cannot be closed again.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyClosedError):
        service.close_episode(
            context=context,
            episode_id=episode.id,
        )


def test_close_episode_rejects_cancelled_episode(
    db,
    hospital,
):
    """
    A CANCELLED Episode cannot be closed.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.cancel_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyCancelledError):
        service.close_episode(
            context=context,
            episode_id=episode.id,
        )


def test_close_episode_rejects_episode_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital must not be able to close another hospital's Episode.
    """

    patient = create_patient(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="PAT-004",
    )

    hospital_two_context = build_context(hospital_two.id)

    service = build_episode_service(db)

    episode = service.create_episode(
        context=hospital_two_context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    hospital_one_context = build_context(hospital.id)

    with pytest.raises(EpisodeNotFoundError):
        service.close_episode(
            context=hospital_one_context,
            episode_id=episode.id,
        )


# =============================================================================
# Cancel
# =============================================================================


def test_cancel_episode_cancels_open_episode(
    db,
    hospital,
):
    """
    An OPEN Episode should transition to CANCELLED.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    cancelled = service.cancel_episode(
        context=context,
        episode_id=episode.id,
    )

    assert cancelled.status == EpisodeStatus.CANCELLED
    assert cancelled.closed_at is None


def test_cancel_episode_rejects_already_cancelled_episode(
    db,
    hospital,
):
    """
    A CANCELLED Episode cannot be cancelled again.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.cancel_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyCancelledError):
        service.cancel_episode(
            context=context,
            episode_id=episode.id,
        )


def test_cancel_episode_rejects_closed_episode(
    db,
    hospital,
):
    """
    A CLOSED Episode cannot be cancelled.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyClosedError):
        service.cancel_episode(
            context=context,
            episode_id=episode.id,
        )


def test_cancel_episode_rejects_admitted_episode(
    db,
    hospital,
):
    """
    An ADMITTED Episode cannot be cancelled.
    """

    (
        context,
        patient,
        staff,
        episode,
        encounter,
        service,
    ) = create_episode_with_encounter(
        db,
        hospital,
    )

    service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
    )

    with pytest.raises(EpisodeAlreadyAdmittedError):
        service.cancel_episode(
            context=context,
            episode_id=episode.id,
        )


def test_cancel_episode_rejects_episode_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital must not be able to cancel another hospital's Episode.
    """

    patient = create_patient(
        db=db,
        hospital_id=hospital_two.id,
        hospital_number="PAT-005",
    )

    hospital_two_context = build_context(hospital_two.id)

    service = build_episode_service(db)

    episode = service.create_episode(
        context=hospital_two_context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    hospital_one_context = build_context(hospital.id)

    with pytest.raises(EpisodeNotFoundError):
        service.cancel_episode(
            context=hospital_one_context,
            episode_id=episode.id,
        )


# =============================================================================
# Patient Episode Listing
# =============================================================================


def test_list_patient_episodes_returns_patient_episodes(
    db,
    hospital,
):
    """
    Episodes should be retrievable through the patient listing.
    """

    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    first = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="First Consultation",
    )

    second = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Follow-up Consultation",
    )

    episodes = service.list_patient_episodes(
        context=context,
        patient_id=patient.id,
    )

    episode_ids = {
        episode.id
        for episode in episodes
    }

    assert first.id in episode_ids
    assert second.id in episode_ids


# =============================================================================
# Episode Check-In
# =============================================================================


def test_check_in_episode_moves_episode_to_nursing_queue(
    db,
    hospital,
):
    """
    Checking in an Episode moves it from AWAITING_CHECK_IN
    to WAITING_FOR_NURSING and records the authenticated Staff member.
    """

    user, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    assert episode.flow_status == EpisodeFlowStatus.AWAITING_CHECK_IN

    checked_in_episode = service.check_in_episode(
        context=context,
        episode_id=episode.id,
    )

    assert (
        checked_in_episode.flow_status
        == EpisodeFlowStatus.WAITING_FOR_NURSING
    )

    assert checked_in_episode.checked_in_by == staff.id

    assert checked_in_episode.checked_in_by != user.id

    assert checked_in_episode.checked_in_at is not None


def test_check_in_episode_rejects_episode_not_awaiting_check_in(
    db,
    hospital,
):
    """
    An Episode that has already entered the nursing queue
    cannot be checked in again.
    """

    _, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.check_in_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeNotAwaitingCheckInError):
        service.check_in_episode(
            context=context,
            episode_id=episode.id,
        )


def test_check_in_episode_rejects_user_without_staff_profile(
    db,
    hospital,
):
    """
    A UserAccount without a Staff profile cannot perform
    Episode check-in.
    """

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"user-{uuid4()}@example.com",
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

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    with pytest.raises(StaffNotFoundError):
        service.check_in_episode(
            context=context,
            episode_id=episode.id,
        )


def test_check_in_episode_rejects_closed_episode(
    db,
    hospital,
):
    """
    A CLOSED Episode cannot be checked in.
    """

    _, _, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyClosedError):
        service.check_in_episode(
            context=context,
            episode_id=episode.id,
        )


def test_check_in_episode_rejects_cancelled_episode(
    db,
    hospital,
):
    """
    A CANCELLED Episode cannot be checked in.
    """

    _, _, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    service.cancel_episode(
        context=context,
        episode_id=episode.id,
    )

    with pytest.raises(EpisodeAlreadyCancelledError):
        service.check_in_episode(
            context=context,
            episode_id=episode.id,
        )