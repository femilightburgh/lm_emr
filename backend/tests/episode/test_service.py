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

from sqlalchemy import select

from app.core.context import RequestContext

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)
from app.modules.clinical_documents.repositories import (
    ClinicalDocumentRepository,
)
from app.modules.clinical_documents.services.clinical_document_service import (
    ClinicalDocumentService,
)

from app.modules.episode.exceptions import (
    EncounterNotBelongingToEpisodeError,
    EncounterNotOpenError,
    EpisodeAlreadyAdmittedError,
    InvalidWardReviewDispositionError,
    WardReviewDispositionDetailsRequiredError,
    WardReviewEncounterRequiredError,
    EpisodeAlreadyCancelledError,
    EpisodeAlreadyClosedError,
    EpisodeNotAwaitingCheckInError,
    EpisodeNotFoundError,
    PatientNotFoundError,
    StaffNotFoundError,
)

from app.modules.episode.models import (
    EpisodeDisposition,
    EpisodeDispositionType,
    EpisodeFlowStatus,
    EpisodeStatus,
)

from app.modules.episode.schemas.request import (
    ConsultationDisposition,
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
from app.modules.events.services.event_service import (
    ClinicalEventService,
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

from app.modules.organization.department_repository import (
    DepartmentRepository,
)
from app.modules.organization.department_service import (
    DepartmentService,
)
from app.modules.organization.enums import (
    DepartmentCategory,
    DepartmentStatus,
)
from app.modules.organization.schemas import (
    DepartmentCreate,
)

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
    *,
    staff_number=None,
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
        staff_number=(
            staff_number
            or f"STF-{uuid4().hex[:8]}"
        ),
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
# Ward Review Test Helpers
# =============================================================================


def create_admitted_ward_review(
    db,
    hospital,
    *,
    hospital_number,
    staff_number,
):
    """
    Create an admitted Episode with an OPEN Ward Review Encounter.
    """

    _, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
        staff_number=staff_number,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number=hospital_number,
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Admission",
    )

    episode.status = EpisodeStatus.ADMITTED
    episode.managing_doctor_id = staff.id

    encounter = create_open_encounter(
        db=db,
        hospital=hospital,
        episode=episode,
        staff=staff,
    )

    encounter.title = "Ward Review"

    db.commit()
    db.refresh(episode)
    db.refresh(encounter)

    return (
        context,
        staff,
        episode,
        encounter,
        service,
    )


# =============================================================================
# Ward Review Completion
# =============================================================================


def test_complete_ward_review_continue_admission(
    db,
    hospital,
):
    """
    Continuing admission closes the Ward Review while keeping the
    Episode ADMITTED.
    """

    (
        context,
        staff,
        episode,
        encounter,
        service,
    ) = create_admitted_ward_review(
        db,
        hospital,
        hospital_number="PAT-WARD-DISP-001",
        staff_number="STF-WARD-DISP-001",
    )

    completed = service.complete_ward_review(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
        disposition=EpisodeDispositionType.CONTINUE_ADMISSION,
    )

    db.refresh(completed)
    db.refresh(encounter)

    disposition = db.scalar(
        select(EpisodeDisposition).where(
            EpisodeDisposition.episode_id == episode.id,
        )
    )

    assert completed.status == EpisodeStatus.ADMITTED
    assert completed.closed_at is None
    assert encounter.status == EncounterStatus.CLOSED
    assert encounter.ended_at is not None
    assert disposition is not None
    assert (
        disposition.disposition
        == EpisodeDispositionType.CONTINUE_ADMISSION
    )
    assert disposition.decided_by == staff.id


def test_complete_ward_review_discharge_closes_episode(
    db,
    hospital,
):
    """
    Discharge closes both the Ward Review Encounter and the Episode.
    """

    (
        context,
        staff,
        episode,
        encounter,
        service,
    ) = create_admitted_ward_review(
        db,
        hospital,
        hospital_number="PAT-WARD-DISP-002",
        staff_number="STF-WARD-DISP-002",
    )

    completed = service.complete_ward_review(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
        disposition=EpisodeDispositionType.DISCHARGE,
    )

    db.refresh(completed)
    db.refresh(encounter)

    disposition = db.scalar(
        select(EpisodeDisposition).where(
            EpisodeDisposition.episode_id == episode.id,
        )
    )

    assert completed.status == EpisodeStatus.CLOSED
    assert completed.closed_at is not None
    assert encounter.status == EncounterStatus.CLOSED
    assert encounter.ended_at is not None
    assert disposition is not None
    assert disposition.disposition == EpisodeDispositionType.DISCHARGE
    assert disposition.decided_by == staff.id


@pytest.mark.parametrize(
    "disposition",
    [
        EpisodeDispositionType.TRANSFER,
        EpisodeDispositionType.REFERRAL,
        EpisodeDispositionType.OTHER,
    ],
)
def test_complete_ward_review_requires_details(
    db,
    hospital,
    disposition,
):
    """
    Transfer, referral, and other dispositions require details.
    """

    (
        context,
        staff,
        episode,
        encounter,
        service,
    ) = create_admitted_ward_review(
        db,
        hospital,
        hospital_number=(
            f"PAT-WD-{disposition.value[:1]}-002"
        ),
        staff_number=(
            f"STF-WD-{disposition.value[:1]}-002"
        ),
    )

    with pytest.raises(
        WardReviewDispositionDetailsRequiredError,
    ):
        service.complete_ward_review(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
            disposition=disposition,
        )

    db.refresh(episode)
    db.refresh(encounter)

    disposition_record = db.scalar(
        select(EpisodeDisposition).where(
            EpisodeDisposition.episode_id == episode.id,
        )
    )

    assert episode.status == EpisodeStatus.ADMITTED
    assert episode.closed_at is None
    assert encounter.status == EncounterStatus.OPEN
    assert encounter.ended_at is None
    assert disposition_record is None


@pytest.mark.parametrize(
    "disposition",
    [
        EpisodeDispositionType.TRANSFER,
        EpisodeDispositionType.REFERRAL,
        EpisodeDispositionType.OTHER,
    ],
)
def test_complete_ward_review_persists_details(
    db,
    hospital,
    disposition,
):
    """
    Transfer, referral, and other dispositions preserve their details.
    """

    (
        context,
        staff,
        episode,
        encounter,
        service,
    ) = create_admitted_ward_review(
        db,
        hospital,
        hospital_number=(
            f"PAT-WD-{disposition.value[:1]}-001"
        ),
        staff_number=(
            f"STF-WD-{disposition.value[:1]}-001"
        ),
    )

    details = "Clinical disposition details."

    completed = service.complete_ward_review(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
        disposition=disposition,
        details=details,
    )

    db.refresh(completed)
    db.refresh(encounter)

    disposition_record = db.scalar(
        select(EpisodeDisposition).where(
            EpisodeDisposition.episode_id == episode.id,
        )
    )

    assert completed.status == EpisodeStatus.ADMITTED
    assert encounter.status == EncounterStatus.CLOSED
    assert disposition_record is not None
    assert disposition_record.details == details
    assert disposition_record.decided_by == staff.id


def test_complete_ward_review_rejects_non_ward_review_encounter(
    db,
    hospital,
):
    """
    Only a Ward Review Encounter can complete the Ward Review workflow.
    """

    (
        context,
        staff,
        episode,
        encounter,
        service,
    ) = create_admitted_ward_review(
        db,
        hospital,
        hospital_number="PAT-WARD-DISP-003",
        staff_number="STF-WARD-DISP-003",
    )

    encounter.title = "Doctor Consultation"
    db.commit()
    db.refresh(encounter)

    with pytest.raises(
        WardReviewEncounterRequiredError,
    ):
        service.complete_ward_review(
            context=context,
            episode_id=episode.id,
            encounter_id=encounter.id,
            disposition=EpisodeDispositionType.DISCHARGE,
        )

    db.refresh(episode)
    db.refresh(encounter)

    disposition_record = db.scalar(
        select(EpisodeDisposition).where(
            EpisodeDisposition.episode_id == episode.id,
        )
    )

    assert episode.status == EpisodeStatus.ADMITTED
    assert encounter.status == EncounterStatus.OPEN
    assert disposition_record is None


def test_complete_ward_review_rejects_wrong_episode_encounter(
    db,
    hospital,
):
    """
    A Ward Review Encounter from another Episode cannot be completed.
    """

    (
        context,
        staff,
        episode,
        encounter,
        service,
    ) = create_admitted_ward_review(
        db,
        hospital,
        hospital_number="PAT-WARD-DISP-004",
        staff_number="STF-WARD-DISP-004",
    )

    other_patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-WARD-DISP-005",
    )

    other_episode = service.create_episode(
        context=context,
        patient_id=other_patient.id,
        title="Medical Admission",
    )

    other_episode.status = EpisodeStatus.ADMITTED
    other_episode.managing_doctor_id = staff.id

    db.commit()
    db.refresh(other_episode)

    with pytest.raises(
        EncounterNotBelongingToEpisodeError,
    ):
        service.complete_ward_review(
            context=context,
            episode_id=other_episode.id,
            encounter_id=encounter.id,
            disposition=EpisodeDispositionType.DISCHARGE,
        )

    db.refresh(episode)
    db.refresh(encounter)
    db.refresh(other_episode)

    assert episode.status == EpisodeStatus.ADMITTED
    assert other_episode.status == EpisodeStatus.ADMITTED
    assert encounter.status == EncounterStatus.OPEN


# =============================================================================
# Episode Routing Transaction Atomicity
# =============================================================================


def test_route_episode_rolls_back_nursing_encounter_closure_on_failure(
    db,
    hospital,
):
    """
    Routing must atomically commit the Episode transition and
    Nursing Encounter closure.

    If routing fails after the Nursing Encounter has been closed
    in the transaction, both changes must be rolled back.
    """

    _, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-ROUTE-ATOMIC-001",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    episode.flow_status = EpisodeFlowStatus.WAITING_FOR_NURSING
    db.commit()
    db.refresh(episode)

    service.start_nursing(
        context=context,
        episode_id=episode.id,
    )

    db.refresh(episode)

    encounter = next(
        encounter
        for encounter in episode.encounters
        if encounter.title == "Nursing Intake"
    )

    assert encounter.status == EncounterStatus.OPEN

    document_service = ClinicalDocumentService(
        repository=ClinicalDocumentRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
    )

    document = document_service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.NURSING_INTAKE,
        authored_by=staff.id,
        content={
            "blood_pressure": "120/80",
            "pulse_rate": 72,
            "temperature": 36.5,
        },
    )

    document_service.sign_document(
        context=context,
        document_id=document.id,
        signed_at=datetime(
            2026,
            8,
            31,
            12,
            0,
            tzinfo=UTC,
        ),
    )

    department_service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    department = department_service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Emergency Department",
            code="ROUTE-ATOMIC-ED",
            category=DepartmentCategory.CLINICAL,
            status=DepartmentStatus.ACTIVE,
        ),
    )

    original_save = service.repository.save

    def failing_save():
        raise RuntimeError("Forced routing transaction failure.")

    service.repository.save = failing_save

    try:
        with pytest.raises(
            RuntimeError,
            match="Forced routing transaction failure",
        ):
            service.route_episode(
                context=context,
                episode_id=episode.id,
                department_id=department.id,
            )
    finally:
        service.repository.save = original_save

    db.expire_all()

    refreshed_episode = db.get(
        type(episode),
        episode.id,
    )

    assert refreshed_episode is not None

    assert (
        refreshed_episode.flow_status
        == EpisodeFlowStatus.NURSING_IN_PROGRESS
    )

    assert refreshed_episode.current_department_id is None
    assert refreshed_episode.routed_at is None
    assert refreshed_episode.routed_by is None

    refreshed_encounter = db.get(
        Encounter,
        encounter.id,
    )

    assert refreshed_encounter is not None
    assert refreshed_encounter.status == EncounterStatus.OPEN
    assert refreshed_encounter.ended_at is None


# =============================================================================
# Doctor Queues
# =============================================================================


def test_list_doctor_clinic_queue_includes_routed_open_episode(
    db,
    hospital,
):
    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-C-001",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    episode.flow_status = EpisodeFlowStatus.ROUTED
    episode.routed_at = datetime.now(UTC)

    db.commit()
    db.refresh(episode)

    results = service.list_doctor_clinic_queue(
        context=context,
    )

    assert episode.id in {
        item.id
        for item in results
    }


def test_list_doctor_clinic_queue_excludes_non_routed_open_episode(
    db,
    hospital,
):
    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-C-002",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    results = service.list_doctor_clinic_queue(
        context=context,
    )

    assert episode.id not in {
        item.id
        for item in results
    }


def test_list_doctor_clinic_queue_excludes_closed_routed_episode(
    db,
    hospital,
):
    context = build_context(hospital.id)

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-C-003",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    episode.flow_status = EpisodeFlowStatus.ROUTED
    episode.status = EpisodeStatus.CLOSED
    episode.routed_at = datetime.now(UTC)

    db.commit()
    db.refresh(episode)

    results = service.list_doctor_clinic_queue(
        context=context,
    )

    assert episode.id not in {
        item.id
        for item in results
    }


def test_list_doctor_ward_queue_includes_managed_admitted_episode(
    db,
    hospital,
):
    _, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-W-001",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    episode.status = EpisodeStatus.ADMITTED
    episode.managing_doctor_id = staff.id

    db.commit()
    db.refresh(episode)

    results = service.list_doctor_ward_queue(
        context=context,
    )

    assert episode.id in {
        item.id
        for item in results
    }


def test_list_doctor_ward_queue_excludes_episode_managed_by_another_doctor(
    db,
    hospital,
):
    _, current_doctor, current_context = (
        create_authenticated_staff(
            db=db,
            hospital=hospital,
        )
    )

    _, other_doctor, _ = (
        create_authenticated_staff(
            db=db,
            hospital=hospital,
        )
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-W-002",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=current_context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    episode.status = EpisodeStatus.ADMITTED
    episode.managing_doctor_id = other_doctor.id

    db.commit()
    db.refresh(episode)

    results = service.list_doctor_ward_queue(
        context=current_context,
    )

    assert episode.id not in {
        item.id
        for item in results
    }

    assert current_doctor.id != other_doctor.id


def test_list_doctor_ward_queue_excludes_open_episode(
    db,
    hospital,
):
    _, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-W-003",
    )

    service = build_episode_service(db)

    episode = service.create_episode(
        context=context,
        patient_id=patient.id,
        title="Medical Consultation",
    )

    episode.managing_doctor_id = staff.id

    db.commit()
    db.refresh(episode)

    results = service.list_doctor_ward_queue(
        context=context,
    )

    assert episode.id not in {
        item.id
        for item in results
    }


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


def test_admit_episode_closes_consultation_encounter(
    db,
    hospital,
):
    """
    Admitting an Episode completes the Doctor Consultation encounter
    through which the admission was performed.

    The Episode transitions to ADMITTED and the consultation Encounter
    is closed atomically.
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
    assert encounter.status == EncounterStatus.CLOSED
    assert encounter.ended_at is not None


def test_complete_consultation_orders_investigations(
    db,
    hospital,
):
    """
    Completing an outpatient Doctor Consultation for investigations
    closes the consultation while keeping the Episode OPEN.
    """

    _, staff, context = create_authenticated_staff(
        db=db,
        hospital=hospital,
        staff_number="STF-DOC-COMPLETE-001",
    )

    service = build_episode_service(
        db,
    )

    patient = create_patient(
        db=db,
        hospital_id=hospital.id,
        hospital_number="PAT-DOC-COMPLETE-001",
    )

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

    encounter.title = "Doctor Consultation"
    db.commit()
    db.refresh(encounter)

    document_service = ClinicalDocumentService(
        repository=ClinicalDocumentRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
    )

    document = document_service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=staff.id,
        content={
            "presenting_complaints": [
                "Fever",
            ],
            "history_of_presenting_complaints": (
                "Two days of fever."
            ),
        },
    )

    signed_at = datetime(
        2026,
        8,
        26,
        15,
        0,
        tzinfo=UTC,
    )

    signed = document_service.sign_document(
        context=context,
        document_id=document.id,
        signed_at=signed_at,
    )

    assert signed.status == ClinicalDocumentStatus.SIGNED

    completed = service.complete_consultation(
        context=context,
        episode_id=episode.id,
        encounter_id=encounter.id,
        disposition=ConsultationDisposition.ORDER_INVESTIGATIONS,
    )

    db.refresh(encounter)

    assert completed.status == EpisodeStatus.OPEN
    assert (
        completed.flow_status
        == EpisodeFlowStatus.AWAITING_INVESTIGATIONS
    )
    assert encounter.status == EncounterStatus.CLOSED
    assert encounter.ended_at is not None
    assert encounter.ended_at > signed_at


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