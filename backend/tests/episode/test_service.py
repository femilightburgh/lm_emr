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
• Episode lifecycle
• Hospital/tenant isolation
• Episode numbering
• Invalid lifecycle transitions
==============================================================================
"""

from datetime import date
from uuid import uuid4

import pytest

from app.core.context import RequestContext
from app.modules.episode.exceptions import (
    EpisodeAlreadyCancelledError,
    EpisodeAlreadyClosedError,
    EpisodeNotFoundError,
    PatientNotFoundError,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import EpisodeService
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)
from app.modules.patients.services.patient_service import PatientService


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


def build_episode_service(db):
    """
    Build an EpisodeService with its production dependencies.
    """
    repository = EpisodeRepository(db)

    return EpisodeService(
        repository=repository,
        patient_repository=PatientRepository(db),
        number_generator=EpisodeNumberGenerator(
            repository=repository,
        ),
    )


def create_patient(
    db,
    hospital_id,
    hospital_number="PAT-001",
):
    """
    Create a patient belonging to the specified hospital.
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
    A hospital must not be able to retrieve another hospital's Episode.
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

    episode_ids = {episode.id for episode in episodes}

    assert first.id in episode_ids
    assert second.id in episode_ids