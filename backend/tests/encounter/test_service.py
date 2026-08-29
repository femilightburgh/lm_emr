from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from app.core.context import RequestContext

from app.modules.encounter.exceptions import (
    EncounterAlreadyClosedError,
    EpisodeNotFoundError,
    EpisodeNotOpenError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.encounter.models import (
    Encounter,
    EncounterStatus,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)

from app.modules.identity.repository import IdentityRepository

from app.modules.episode.models import EpisodeStatus
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


def test_create_encounter_creates_open_encounter(
    db,
    hospital,
):
    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    # --------------------------------------------------------------
    # Create Patient
    # --------------------------------------------------------------

    patient_service = PatientService(
        repository=PatientRepository(db),
    )

    patient = patient_service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number="PAT-001",
            first_name="John",
            last_name="Doe",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )

    # --------------------------------------------------------------
    # Create Staff
    # --------------------------------------------------------------

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-ENC-001",
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

    # --------------------------------------------------------------
    # Create Episode
    # --------------------------------------------------------------

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
        title="Diabetic Foot Infection",
    )

    # --------------------------------------------------------------
    # Encounter
    # --------------------------------------------------------------

    service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    encounter = service.create_encounter(
        context=context,
        episode_id=episode.id,
        staff_id=staff.id,
        title="Doctor Ward Round",
    )

    assert encounter.id is not None
    assert encounter.episode_id == episode.id
    assert encounter.staff_id == staff.id
    assert encounter.title == "Doctor Ward Round"
    assert encounter.status.value == "OPEN"
    assert encounter.started_at is not None
    assert encounter.ended_at is None



def test_list_doctor_queue_returns_only_active_doctor_encounters(
    db,
    hospital,
):
    from app.modules.identity.models import UserAccount

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"doctor-{uuid4()}@example.com",
        password_hash="test",
    )
    db.add(user)
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STF-QUEUE-{uuid4().hex[:8]}",
            first_name="Doctor",
            last_name="Queue",
            gender=Gender.MALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff_service.link_user_account(
        staff.id,
        user.id,
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

    patient = PatientService(
        repository=PatientRepository(db),
    ).create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=f"PAT-{uuid4().hex[:8]}",
            first_name="Queue",
            last_name="Patient",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )

    episode = episode_service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Doctor Queue Episode",
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
        title="Doctor Consultation",
    )

    results = encounter_service.list_doctor_queue(
        context=context,
    )

    assert [item.id for item in results] == [encounter.id]


def test_list_doctor_queue_excludes_closed_encounters(
    db,
    hospital,
):
    from app.modules.identity.models import UserAccount

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"doctor-{uuid4()}@example.com",
        password_hash="test",
    )
    db.add(user)
    db.flush()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STF-QUEUE-{uuid4().hex[:8]}",
            first_name="Doctor",
            last_name="Closed",
            gender=Gender.MALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff_service.link_user_account(
        staff.id,
        user.id,
    )

    patient = PatientService(
        repository=PatientRepository(db),
    ).create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=f"PAT-{uuid4().hex[:8]}",
            first_name="Closed",
            last_name="Encounter",
            sex="Female",
            date_of_birth=date(1990, 1, 1),
        ),
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
        title="Closed Encounter Episode",
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
        title="Closed Doctor Encounter",
    )

    encounter_service.close_encounter(
        context=context,
        encounter_id=encounter.id,
    )

    results = encounter_service.list_doctor_queue(
        context=context,
    )

    assert results == []


def test_list_doctor_queue_excludes_other_doctors(
    db,
    hospital,
):
    from app.modules.identity.models import UserAccount

    user_one = UserAccount(
        hospital_id=hospital.id,
        email=f"doctor-one-{uuid4()}@example.com",
        password_hash="test",
    )

    user_two = UserAccount(
        hospital_id=hospital.id,
        email=f"doctor-two-{uuid4()}@example.com",
        password_hash="test",
    )

    db.add_all([user_one, user_two])
    db.flush()

    context_one = RequestContext(
        user_id=user_one.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    context_two = RequestContext(
        user_id=user_two.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff_one = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STF-Q1-{uuid4().hex[:8]}",
            first_name="Doctor",
            last_name="One",
            gender=Gender.MALE,
            date_of_birth=date(1988, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff_service.link_user_account(
        staff_one.id,
        user_one.id,
    )

    staff_two = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STF-Q2-{uuid4().hex[:8]}",
            first_name="Doctor",
            last_name="Two",
            gender=Gender.FEMALE,
            date_of_birth=date(1989, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    staff_service.link_user_account(
        staff_two.id,
        user_two.id,
    )

    patient_service = PatientService(
        repository=PatientRepository(db),
    )

    patient = patient_service.create_patient(
        context=context_one,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=f"PAT-{uuid4().hex[:8]}",
            first_name="Shared",
            last_name="Queue",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
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
        context=context_one,
        patient_id=patient.id,
        title="Shared Queue Episode",
    )

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    encounter_service.create_encounter(
        context=context_one,
        episode_id=episode.id,
        staff_id=staff_one.id,
        title="Doctor One Encounter",
    )

    encounter_service.create_encounter(
        context=context_two,
        episode_id=episode.id,
        staff_id=staff_two.id,
        title="Doctor Two Encounter",
    )

    results = encounter_service.list_doctor_queue(
        context=context_one,
    )

    assert len(results) == 1
    assert results[0].staff_id == staff_one.id


def test_create_encounter_rejects_closed_episode(
    db,
    hospital,
):
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
            hospital_number="PAT-002",
            first_name="Mary",
            last_name="Brown",
            sex="Female",
            date_of_birth=date(1985, 3, 15),
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
            staff_number="STF-ENC-002",
            first_name="David",
            last_name="Jones",
            gender=Gender.MALE,
            date_of_birth=date(1988, 6, 20),
            profession=Profession.NURSE,
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
        title="Diabetic Foot Infection",
    )

    episode_service.close_episode(
        context=context,
        episode_id=episode.id,
    )

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    with pytest.raises(EpisodeNotOpenError):
        encounter_service.create_encounter(
            context=context,
            episode_id=episode.id,
            staff_id=staff.id,
            title="Nurse Medication",
        )


def test_create_encounter_rejects_staff_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
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
            hospital_number="PAT-003",
            first_name="Grace",
            last_name="Williams",
            sex="Female",
            date_of_birth=date(1990, 4, 12),
        ),
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
        title="Diabetic Foot Infection",
    )

    # --------------------------------------------------------------
    # Staff belongs to Hospital B
    # --------------------------------------------------------------

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital_two.id,
            staff_number="STF-ENC-003",
            first_name="Samuel",
            last_name="Adeyemi",
            gender=Gender.MALE,
            date_of_birth=date(1987, 8, 20),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    with pytest.raises(StaffHospitalMismatchError):
        encounter_service.create_encounter(
            context=context,
            episode_id=episode.id,
            staff_id=staff.id,
            title="Nurse Medication",
        )


def test_create_encounter_rejects_missing_staff(
    db,
    hospital,
):
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
            hospital_number="PAT-004",
            first_name="Daniel",
            last_name="Okafor",
            sex="Male",
            date_of_birth=date(1982, 9, 10),
        ),
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
        title="Medical Consultation",
    )

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    with pytest.raises(StaffNotFoundError):
        encounter_service.create_encounter(
            context=context,
            episode_id=episode.id,
            staff_id=uuid4(),
            title="Doctor Consultation",
        )


def test_close_encounter_closes_open_encounter(
    db,
    hospital,
):
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
            hospital_number="PAT-005",
            first_name="Peter",
            last_name="Ade",
            sex="Male",
            date_of_birth=date(1980, 2, 10),
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
            staff_number="STF-ENC-005",
            first_name="Helen",
            last_name="Smith",
            gender=Gender.FEMALE,
            date_of_birth=date(1989, 5, 20),
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
        title="Medical Consultation",
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
        title="Doctor Consultation",
    )

    closed = encounter_service.close_encounter(
        context=context,
        encounter_id=encounter.id,
    )

    assert closed.id == encounter.id
    assert closed.status == EncounterStatus.CLOSED
    assert closed.ended_at is not None


def test_close_encounter_rejects_already_closed_encounter(
    db,
    hospital,
):
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
            hospital_number="PAT-006",
            first_name="Rose",
            last_name="James",
            sex="Female",
            date_of_birth=date(1987, 6, 14),
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
            staff_number="STF-ENC-006",
            first_name="Mark",
            last_name="Williams",
            gender=Gender.MALE,
            date_of_birth=date(1985, 3, 12),
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
        title="Medical Consultation",
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
        title="Doctor Consultation",
    )

    encounter_service.close_encounter(
        context=context,
        encounter_id=encounter.id,
    )

    with pytest.raises(EncounterAlreadyClosedError):
        encounter_service.close_encounter(
            context=context,
            encounter_id=encounter.id,
        )


def test_create_encounter_rejects_missing_episode(
    db,
    hospital,
):
    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-ENC-007",
            first_name="James",
            last_name="Brown",
            gender=Gender.MALE,
            date_of_birth=date(1986, 4, 18),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    with pytest.raises(EpisodeNotFoundError):
        encounter_service.create_encounter(
            context=context,
            episode_id=uuid4(),
            staff_id=staff.id,
            title="Doctor Consultation",
        )


def test_create_encounter_allows_admitted_episode(
    db,
    hospital,
):
    """
    An ADMITTED Episode should continue to accept new Encounters.

    Admission does not end the Episode's clinical activity.
    Additional professional Encounters may occur throughout
    the patient's admission.
    """

    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    # --------------------------------------------------------------
    # Create Patient
    # --------------------------------------------------------------

    patient_service = PatientService(
        repository=PatientRepository(db),
    )

    patient = patient_service.create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number="PAT-ADM-001",
            first_name="John",
            last_name="Doe",
            sex="Male",
            date_of_birth=date(1990, 1, 1),
        ),
    )

    # --------------------------------------------------------------
    # Create Staff
    # --------------------------------------------------------------

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-ADM-001",
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

    # --------------------------------------------------------------
    # Create Episode
    # --------------------------------------------------------------

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
        title="Diabetic Foot Infection",
    )

    # --------------------------------------------------------------
    # Admit Episode
    # --------------------------------------------------------------

    admission_encounter = Encounter(
        episode_id=episode.id,
        staff_id=staff.id,
        title="Admission Assessment",
        status=EncounterStatus.OPEN,
        started_at=datetime.now(UTC),
        ended_at=None,
    )

    db.add(admission_encounter)
    db.commit()
    db.refresh(admission_encounter)

    episode_service.admit_episode(
        context=context,
        episode_id=episode.id,
        encounter_id=admission_encounter.id,
    )

    # --------------------------------------------------------------
    # Create Encounter After Admission
    # --------------------------------------------------------------

    encounter_service = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    )

    encounter = encounter_service.create_encounter(
        context=context,
        episode_id=episode.id,
        staff_id=staff.id,
        title="Doctor Ward Round",
    )

    # --------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------

    assert episode.status == EpisodeStatus.ADMITTED
    assert encounter.id is not None
    assert encounter.episode_id == episode.id
    assert encounter.staff_id == staff.id
    assert encounter.title == "Doctor Ward Round"
    assert encounter.status == EncounterStatus.OPEN
    assert encounter.started_at is not None
    assert encounter.ended_at is None