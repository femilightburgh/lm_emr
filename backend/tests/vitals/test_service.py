"""
==============================================================================
LIGHTBURGH EMR

Vitals Service Tests
==============================================================================

Tests the business logic for recording patient vital signs.

Clinical hierarchy:

Patient
    ↓
Episode
    ↓
Encounter
    ↓
Clinical Event
    ↓
Vitals
==============================================================================
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.context import RequestContext
from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount

from app.modules.events.enums import EventType
from app.modules.events.exceptions import (
    EncounterNotFoundError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService

from app.modules.vitals.schemas import CreateVitalsRequest
from app.modules.vitals.services import VitalsService

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

from app.modules.organization.repository import HospitalRepository


# ============================================================================
# Test Data Helper
# ============================================================================


def create_test_encounter(
    db,
    hospital,
):
    """
    Create the minimum valid Patient → Episode → Staff → Encounter
    hierarchy required by the Vitals service.
    """

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"vitals-{uuid4()}@example.com",
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
            hospital_number=f"PAT-VITALS-{uuid4().hex[:8]}",
            first_name="Vitals",
            last_name="Patient",
            sex="Male",
            date_of_birth=datetime(1990, 1, 1).date(),
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
            staff_number=f"STF-VITALS-{uuid4().hex[:8]}",
            first_name="Vitals",
            last_name="Clinician",
            gender=Gender.MALE,
            date_of_birth=datetime(1985, 1, 1).date(),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=datetime(2026, 1, 1).date(),
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
# Service Helper
# ============================================================================


def create_vitals_service(db):
    """
    Build a VitalsService using the existing ClinicalEventService.
    """

    event_service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    return VitalsService(
        event_service=event_service,
        staff_repository=StaffRepository(db),
    )


# ============================================================================
# Tests
# ============================================================================


def test_record_vitals_creates_clinical_event(
    db,
    hospital,
):
    """
    Recording vitals should create a ClinicalEvent with
    VITALS_RECORDED as its event type.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_vitals_service(db)

    occurred_at = datetime(
        2026,
        8,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )

    request = CreateVitalsRequest(
        encounter_id=encounter.id,
        performed_by=staff.id,
        occurred_at=occurred_at,
        temperature=38.2,
        heart_rate=104,
        respiratory_rate=22,
        systolic_bp=145,
        diastolic_bp=92,
        spo2=96,
        weight=72.5,
    )

    event = service.record_vitals(
        context=context,
        request=request,
    )

    assert event.id is not None
    assert event.encounter_id == encounter.id
    assert event.performed_by == staff.id
    assert event.event_type == EventType.VITALS_RECORDED
    assert event.occurred_at == occurred_at

    assert event.payload == {
        "temperature": 38.2,
        "heart_rate": 104,
        "respiratory_rate": 22,
        "systolic_bp": 145,
        "diastolic_bp": 92,
        "spo2": 96,
        "weight": 72.5,
    }


def test_record_vitals_supports_partial_measurements(
    db,
    hospital,
):
    """
    Vitals may contain only the measurements that were actually obtained.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_vitals_service(db)

    request = CreateVitalsRequest(
        encounter_id=encounter.id,
        performed_by=staff.id,
        occurred_at=datetime.now(timezone.utc),
        temperature=38.4,
    )

    event = service.record_vitals(
        context=context,
        request=request,
    )

    assert event.event_type == EventType.VITALS_RECORDED

    assert event.payload == {
        "temperature": 38.4,
    }


def test_record_vitals_rejects_missing_encounter(
    db,
    hospital,
):
    """
    Vitals cannot be recorded against an encounter that does not exist.
    """

    context, _, _ = create_test_encounter(
        db,
        hospital,
    )

    service = create_vitals_service(db)

    request = CreateVitalsRequest(
        encounter_id=uuid4(),
        performed_by=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        temperature=37.2,
    )

    with pytest.raises(EncounterNotFoundError):
        service.record_vitals(
            context=context,
            request=request,
        )


def test_record_vitals_rejects_authenticated_user_without_staff_profile(
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
        email=f"no-staff-{uuid4()}@example.com",
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

    service = create_vitals_service(db)

    request = CreateVitalsRequest(
        encounter_id=encounter.id,
        performed_by=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        temperature=37.2,
    )

    with pytest.raises(StaffNotFoundError):
        service.record_vitals(
            context=context,
            request=request,
        )


def test_record_vitals_rejects_authenticated_user_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A user whose Staff profile belongs to another hospital is not
    a Staff member of the authenticated hospital.
    """

    from app.modules.identity.enums import AccountStatus
    from app.modules.identity.models import UserAccount

    context, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    user = UserAccount(
        hospital_id=hospital_two.id,
        email=f"foreign-{uuid4()}@example.com",
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
            last_name="Clinician",
            gender=Gender.MALE,
            date_of_birth=datetime(1985, 1, 1).date(),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=datetime(2026, 1, 1).date(),
        )
    )

    foreign_staff.user_account_id = user.id
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = create_vitals_service(db)

    request = CreateVitalsRequest(
        encounter_id=encounter.id,
        performed_by=foreign_staff.id,
        occurred_at=datetime.now(timezone.utc),
        temperature=37.2,
    )

    with pytest.raises(StaffNotFoundError):
        service.record_vitals(
            context=context,
            request=request,
        )


def test_record_vitals_preserves_occurrence_time(
    db,
    hospital,
):
    """
    The time the vitals were actually taken must be preserved.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_vitals_service(db)

    occurred_at = datetime(
        2026,
        8,
        10,
        6,
        45,
        tzinfo=timezone.utc,
    )

    request = CreateVitalsRequest(
        encounter_id=encounter.id,
        performed_by=staff.id,
        occurred_at=occurred_at,
        temperature=36.8,
    )

    event = service.record_vitals(
        context=context,
        request=request,
    )

    assert event.occurred_at == occurred_at


def test_record_vitals_does_not_store_missing_measurements(
    db,
    hospital,
):
    """
    Measurements not supplied by the clinician should not appear
    in the ClinicalEvent payload.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_vitals_service(db)

    request = CreateVitalsRequest(
        encounter_id=encounter.id,
        performed_by=staff.id,
        occurred_at=datetime.now(timezone.utc),
        heart_rate=80,
        spo2=98,
    )

    event = service.record_vitals(
        context=context,
        request=request,
    )

    assert event.payload == {
        "heart_rate": 80,
        "spo2": 98,
    }