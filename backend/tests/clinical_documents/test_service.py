"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Service Tests
==============================================================================

Tests the business logic for Clinical Documents.

Clinical Document lifecycle:

    DRAFT
      |
      | sign
      v
    SIGNED
      |
      | amend
      v
    DRAFT v2
      |
      | sign
      v
    SIGNED v2

Coverage
--------

• Draft creation
• Hospital tenancy
• Document retrieval
• Encounter document listing
• Version history
• Document signing
• Clinical Event generation on signing
• Signed document immutability
• Document amendment
• Amendment versioning
• Signing amended documents
• Atomic rollback when event creation fails
==============================================================================
"""

from datetime import date, datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.core.context import RequestContext

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)
from app.modules.clinical_documents.exceptions import (
    ClinicalDocumentNotFoundError,
    ClinicalDocumentNotLatestVersionError,
    DocumentNotDraftError,
    DocumentNotSignedError,
    EncounterClosedError,
    EncounterNotFoundError,
    EpisodeNotAdmittedError,
    NotManagingDoctorError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.clinical_documents.repositories import (
    ClinicalDocumentRepository,
)
from app.modules.clinical_documents.services.clinical_document_service import (
    ClinicalDocumentService,
)

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)
from app.modules.encounter.models import EncounterStatus
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

from app.modules.events.enums import EventType
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.patients.schemas.patient_schema import (
    CreatePatientRequest,
)
from app.modules.patients.services.patient_service import (
    PatientService,
)

from app.modules.organization.repository import HospitalRepository

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
    hospital_number: str,
    staff_number: str,
):
    """
    Create the minimum valid Patient → Episode → Staff → Encounter
    hierarchy required by the Clinical Document Service.
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
            first_name="Clinical",
            last_name="Document Patient",
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
            first_name="Clinical",
            last_name="Document Clinician",
            gender=Gender.MALE,
            date_of_birth=date(1985, 1, 1),
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
        title="Clinical Document Test Episode",
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
        title="Clinical Document Test Encounter",
    )

    return context, staff, encounter


def create_service(db):
    """
    Construct a ClinicalDocumentService using real repositories and
    ClinicalEventService.
    """

    event_service = ClinicalEventService(
        repository=ClinicalEventRepository(db),
    )

    return ClinicalDocumentService(
        repository=ClinicalDocumentRepository(db),
        event_service=event_service,
    )


def create_document(
    db,
    hospital,
    *,
    hospital_number: str,
    staff_number: str,
    content: dict | None = None,
):
    """
    Create a test encounter and a DRAFT Clinical Document.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number=hospital_number,
        staff_number=staff_number,
    )

    service = create_service(db)

    if content is None:
        content = {
            "presenting_complaints": [
                "Fever",
                "Headache",
            ],
            "history_of_presenting_complaints": (
                "Patient reports two days of fever and headache."
            ),
        }

    document = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=staff.id,
        content=content,
    )

    return context, staff, encounter, document, service


# ============================================================================
# Draft Editing
# ============================================================================


def test_update_draft_changes_content_without_creating_new_version(
    db,
    hospital,
):
    """
    Updating a DRAFT Clinical Document should modify the existing row.

    The document ID and version must remain unchanged.
    """

    context, staff, _, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-018",
        staff_number="STF-CD-SVC-018",
    )

    original_id = document.id
    original_version = document.version
    original_author = document.authored_by
    original_type = document.document_type

    updated_content = {
        "presenting_complaints": [
            "Fever",
            "Headache",
            "Cough",
        ],
        "history_of_presenting_complaints": (
            "Updated history following further clinical assessment."
        ),
    }

    updated = service.update_draft(
        context=context,
        document_id=document.id,
        edited_by=staff.id,
        content=updated_content,
    )

    assert updated.id == original_id
    assert updated.version == original_version
    assert updated.authored_by == original_author
    assert updated.document_type == original_type
    assert updated.status == ClinicalDocumentStatus.DRAFT
    assert updated.content == updated_content


def test_update_draft_does_not_create_clinical_event(
    db,
    hospital,
):
    """
    Editing a DRAFT Clinical Document must not create a Clinical Event.

    A CLINICAL_NOTE_RECORDED event is generated only when the document
    becomes SIGNED.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-019",
        staff_number="STF-CD-SVC-019",
    )

    updated_content = {
        "presenting_complaints": ["Fever"],
        "history_of_presenting_complaints": "Updated draft content.",
    }

    service.update_draft(
        context=context,
        document_id=document.id,
        edited_by=staff.id,
        content=updated_content,
    )

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert events == []


def test_signed_document_cannot_be_updated_as_draft(
    db,
    hospital,
):
    """
    A SIGNED Clinical Document cannot be edited through the draft update
    operation.

    The signed document must remain unchanged.
    """

    context, staff, _, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-020",
        staff_number="STF-CD-SVC-020",
    )

    original_content = dict(document.content)

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    with pytest.raises(DocumentNotDraftError):
        service.update_draft(
            context=context,
            document_id=document.id,
            edited_by=staff.id,
            content={
                "presenting_complaints": ["Changed after signing"],
                "history_of_presenting_complaints": (
                    "This update must be rejected."
                ),
            },
        )

    db.expire_all()

    persisted_document = db.get(
        type(document),
        document.id,
    )

    assert persisted_document.status == ClinicalDocumentStatus.SIGNED
    assert persisted_document.content == original_content
    assert persisted_document.version == 1
    assert persisted_document.signed_by == staff.id


def test_update_draft_rejects_editor_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A staff member belonging to another hospital cannot update a draft
    Clinical Document.
    """

    context, _, _, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-021",
        staff_number="STF-CD-SVC-021",
    )

    foreign_staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    foreign_staff = foreign_staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital_two.id,
            staff_number="STF-CD-FOREIGN-001",
            first_name="Foreign",
            last_name="Clinician",
            gender=Gender.MALE,
            date_of_birth=date(1985, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    original_content = dict(document.content)

    with pytest.raises(StaffHospitalMismatchError):
        service.update_draft(
            context=context,
            document_id=document.id,
            edited_by=foreign_staff.id,
            content={
                "presenting_complaints": ["Unauthorized update"],
                "history_of_presenting_complaints": (
                    "This update must be rejected."
                ),
            },
        )

    db.expire_all()

    persisted_document = db.get(
        type(document),
        document.id,
    )

    assert persisted_document.status == ClinicalDocumentStatus.DRAFT
    assert persisted_document.content == original_content


# ============================================================================
# Create Draft
# ============================================================================


def test_create_draft(
    db,
    hospital,
):
    """
    A valid Clinical Document should be created as DRAFT.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-001",
        staff_number="STF-CD-SVC-001",
    )

    service = create_service(db)

    content = {
        "presenting_complaints": ["Fever"],
        "history_of_presenting_complaints": "Two days of fever.",
    }

    document = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=staff.id,
        content=content,
    )

    assert document.id is not None
    assert document.encounter_id == encounter.id
    assert document.document_type == ClinicalDocumentType.INITIAL_CLERKING
    assert document.status == ClinicalDocumentStatus.DRAFT
    assert document.version == 1
    assert document.authored_by == staff.id
    assert document.signed_at is None
    assert document.signed_by is None
    assert document.amended_from_id is None
    assert document.content == content


def test_create_draft_serializes_structured_clinical_content(
    db,
    hospital,
):
    """
    A Pydantic Clinical Document content schema should be serialized
    into JSON-compatible data before persistence.
    """

    from app.modules.clinical_documents.schemas import (
        InitialClerkingContent,
    )

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-017",
        staff_number="STF-CD-SVC-017",
    )

    service = create_service(db)

    content = InitialClerkingContent(
        presenting_complaints=[
            {
                "complaint": "Fever",
                "duration": "3 days",
            },
        ],
        history_of_presenting_complaint=(
            "Patient developed fever three days ago."
        ),
        examination={
            "general": "Conscious and alert.",
            "cardiovascular": "S1 and S2 heard.",
        },
        assessment={
            "working_diagnosis": "Malaria",
            "differentials": [
                "Typhoid fever",
            ],
        },
    )

    document = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=staff.id,
        content=content,
    )

    assert document.content == content.model_dump(mode="json")


# ============================================================================
# Tenancy
# ============================================================================


def test_create_draft_rejects_encounter_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital cannot create a Clinical Document against another
    hospital's Encounter.
    """

    context_a, _, _ = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-002",
        staff_number="STF-CD-SVC-002",
    )

    _, staff_b, encounter_b = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-CD-SVC-003",
        staff_number="STF-CD-SVC-003",
    )

    service = create_service(db)

    with pytest.raises(EncounterNotFoundError):
        service.create_draft(
            context=context_a,
            encounter_id=encounter_b.id,
            document_type=ClinicalDocumentType.INITIAL_CLERKING,
            authored_by=staff_b.id,
            content={"history": "Test"},
        )


def test_create_draft_rejects_author_from_another_hospital(
    db,
    hospital,
    hospital_two,
):
    """
    A hospital cannot create a document using a Staff member from
    another hospital.
    """

    context_a, _, encounter_a = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-004",
        staff_number="STF-CD-SVC-004",
    )

    _, staff_b, _ = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-CD-SVC-005",
        staff_number="STF-CD-SVC-005",
    )

    service = create_service(db)

    with pytest.raises(StaffHospitalMismatchError):
        service.create_draft(
            context=context_a,
            encounter_id=encounter_a.id,
            document_type=ClinicalDocumentType.INITIAL_CLERKING,
            authored_by=staff_b.id,
            content={"history": "Test"},
        )


# ============================================================================
# Retrieval
# ============================================================================


def test_get_document(
    db,
    hospital,
):
    """
    A Clinical Document should be retrievable within its hospital.
    """

    context, _, _, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-006",
        staff_number="STF-CD-SVC-006",
    )

    result = service.get_document(
        context=context,
        document_id=document.id,
    )

    assert result.id == document.id


def test_get_missing_document_raises_not_found(
    db,
    hospital,
):
    """
    Retrieving an unknown Clinical Document should raise the
    domain-specific not-found exception.
    """

    context, _, _, _, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-007",
        staff_number="STF-CD-SVC-007",
    )

    with pytest.raises(ClinicalDocumentNotFoundError):
        service.get_document(
            context=context,
            document_id=uuid4(),
        )


def test_list_encounter_documents(
    db,
    hospital,
):
    """
    Documents belonging to an Encounter should be returned.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-008",
        staff_number="STF-CD-SVC-008",
    )

    service = create_service(db)

    first = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=staff.id,
        content={"history": "Initial"},
    )

    second = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.PROGRESS_NOTE,
        authored_by=staff.id,
        content={"progress": "Improving"},
    )

    documents = service.list_encounter_documents(
        context=context,
        encounter_id=encounter.id,
    )

    document_ids = {document.id for document in documents}

    assert first.id in document_ids
    assert second.id in document_ids


# ============================================================================
# Signing
# ============================================================================


def test_sign_document(
    db,
    hospital,
):
    """
    Signing a DRAFT document should make it SIGNED and record the
    signing metadata.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-009",
        staff_number="STF-CD-SVC-009",
    )

    signed_at = datetime(
        2026,
        8,
        15,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
        signed_at=signed_at,
    )

    assert result.status == ClinicalDocumentStatus.SIGNED
    assert result.signed_by == staff.id
    assert result.signed_at == signed_at


def test_sign_document_creates_clinical_event(
    db,
    hospital,
):
    """
    Signing a Clinical Document should create exactly one
    CLINICAL_NOTE_RECORDED event.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-010",
        staff_number="STF-CD-SVC-010",
    )

    signed_at = datetime(
        2026,
        8,
        15,
        13,
        0,
        tzinfo=timezone.utc,
    )

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
        signed_at=signed_at,
    )

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type == EventType.CLINICAL_NOTE_RECORDED
    assert event.performed_by == staff.id
    assert event.occurred_at == signed_at

    assert event.payload["clinical_document_id"] == str(document.id)
    assert event.payload["document_type"] == (
        ClinicalDocumentType.INITIAL_CLERKING.value
    )
    assert event.payload["version"] == 1


def test_signed_document_cannot_be_signed_again(
    db,
    hospital,
):
    """
    A SIGNED Clinical Document cannot be signed a second time.
    """

    context, staff, _, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-011",
        staff_number="STF-CD-SVC-011",
    )

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    with pytest.raises(DocumentNotDraftError):
        service.sign_document(
            context=context,
            document_id=document.id,
            signed_by=staff.id,
        )


# ============================================================================
# Amendment
# ============================================================================


def test_signed_document_can_be_amended(
    db,
    hospital,
):
    """
    Amending a SIGNED document should create a new DRAFT version.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-012",
        staff_number="STF-CD-SVC-012",
    )

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    amended_content = {
        "presenting_complaints": ["Fever", "Headache"],
        "history_of_presenting_complaints": (
            "Updated clinical history."
        ),
    }

    amended = service.amend_document(
        context=context,
        document_id=document.id,
        authored_by=staff.id,
        content=amended_content,
    )

    assert amended.id != document.id
    assert amended.encounter_id == encounter.id
    assert amended.document_type == document.document_type
    assert amended.version == 2
    assert amended.status == ClinicalDocumentStatus.DRAFT
    assert amended.authored_by == staff.id
    assert amended.amended_from_id == document.id
    assert amended.content == amended_content

    # Original remains signed and unchanged.
    assert document.status == ClinicalDocumentStatus.SIGNED
    assert document.version == 1
    assert document.content != amended_content


def test_draft_document_cannot_be_amended(
    db,
    hospital,
):
    """
    Only SIGNED documents can be amended.
    """

    context, staff, _, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-013",
        staff_number="STF-CD-SVC-013",
    )

    with pytest.raises(DocumentNotSignedError):
        service.amend_document(
            context=context,
            document_id=document.id,
            authored_by=staff.id,
            content={"history": "Invalid amendment"},
        )


def test_list_versions_returns_document_history(
    db,
    hospital,
):
    """
    Version history should contain the original document and its
    amendment.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-014",
        staff_number="STF-CD-SVC-014",
    )

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    amended = service.amend_document(
        context=context,
        document_id=document.id,
        authored_by=staff.id,
        content={"history": "Updated"},
    )

    versions = service.list_versions(
        context=context,
        encounter_id=encounter.id,
        document_type=document.document_type,
    )

    versions_by_number = {
        version.version: version
        for version in versions
    }

    assert 1 in versions_by_number
    assert 2 in versions_by_number

    assert versions_by_number[1].id == document.id
    assert versions_by_number[2].id == amended.id


def test_sign_amended_document_creates_second_event(
    db,
    hospital,
):
    """
    Signing an amended document should create another
    CLINICAL_NOTE_RECORDED event for the new version.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-015",
        staff_number="STF-CD-SVC-015",
    )

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    amended = service.amend_document(
        context=context,
        document_id=document.id,
        authored_by=staff.id,
        content={"history": "Amended history"},
    )

    amended_signed_at = datetime(
        2026,
        8,
        15,
        15,
        0,
        tzinfo=timezone.utc,
    )

    service.sign_document(
        context=context,
        document_id=amended.id,
        signed_by=staff.id,
        signed_at=amended_signed_at,
    )

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert len(events) == 2

    assert all(
        event.event_type == EventType.CLINICAL_NOTE_RECORDED
        for event in events
    )

    events_by_version = {
        event.payload["version"]: event
        for event in events
    }

    assert events_by_version[1].payload["clinical_document_id"] == str(
        document.id,
    )

    assert events_by_version[2].payload["clinical_document_id"] == str(
        amended.id,
    )


# ============================================================================
# Atomic Transaction
# ============================================================================


def test_sign_document_rolls_back_if_event_creation_fails(
    db,
    hospital,
):
    """
    Signing a document and creating its Clinical Event must be atomic.

    If Clinical Event creation fails:

        • document remains DRAFT
        • signed_at remains NULL
        • signed_by remains NULL
        • no Clinical Event remains persisted
    """

    context, staff, encounter, document, _ = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-SVC-016",
        staff_number="STF-CD-SVC-016",
    )

    failing_event_service = Mock()

    failing_event_service.create_event.side_effect = RuntimeError(
        "Simulated event creation failure.",
    )

    service = ClinicalDocumentService(
        repository=ClinicalDocumentRepository(db),
        event_service=failing_event_service,
    )

    signed_at = datetime(
        2026,
        8,
        15,
        16,
        0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(RuntimeError):
        service.sign_document(
            context=context,
            document_id=document.id,
            signed_by=staff.id,
            signed_at=signed_at,
        )

    # ------------------------------------------------------------------
    # Reload Document
    # ------------------------------------------------------------------

    db.expire_all()

    persisted_document = db.get(
        type(document),
        document.id,
    )

    assert persisted_document.status == ClinicalDocumentStatus.DRAFT
    assert persisted_document.signed_at is None
    assert persisted_document.signed_by is None

    # ------------------------------------------------------------------
    # Verify No Event Was Persisted
    # ------------------------------------------------------------------

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert events == []

    failing_event_service.create_event.assert_called_once()


def test_amend_document_rejects_non_latest_signed_version(
    db,
    hospital,
):
    """
    Only the latest signed version of a Clinical Document may be amended.

    Scenario:

        v1 SIGNED
          ↓
        amend
          ↓
        v2 DRAFT
          ↓
        sign
          ↓
        v2 SIGNED

    Attempting to amend v1 must be rejected because v2 is now
    the latest version.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-LATEST-001",
        staff_number="STF-CD-LATEST-001",
    )

    # ------------------------------------------------------------------
    # Sign version 1
    # ------------------------------------------------------------------

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    # ------------------------------------------------------------------
    # Create version 2
    # ------------------------------------------------------------------

    version_two = service.amend_document(
        context=context,
        document_id=document.id,
        authored_by=staff.id,
        content={
            "presenting_complaints": [
                "Updated complaint",
            ],
            "history_of_presenting_complaints": (
                "Updated clinical history."
            ),
        },
    )

    assert version_two.version == 2
    assert version_two.status == ClinicalDocumentStatus.DRAFT
    assert version_two.amended_from_id == document.id

    # ------------------------------------------------------------------
    # Sign version 2
    # ------------------------------------------------------------------

    service.sign_document(
        context=context,
        document_id=version_two.id,
        signed_by=staff.id,
    )

    # ------------------------------------------------------------------
    # Version 1 is now historical and must not be amendable.
    # ------------------------------------------------------------------

    with pytest.raises(
        ClinicalDocumentNotLatestVersionError,
    ):
        service.amend_document(
            context=context,
            document_id=document.id,
            authored_by=staff.id,
            content={
                "presenting_complaints": [
                    "Illegal amendment",
                ],
                "history_of_presenting_complaints": (
                    "This amendment must be rejected."
                ),
            },
        )

    # ------------------------------------------------------------------
    # Verify version history remains intact.
    # ------------------------------------------------------------------

    versions = service.list_versions(
        context=context,
        encounter_id=encounter.id,
        document_type=document.document_type,
    )

    assert len(versions) == 2

    versions_by_number = {
        version.version: version
        for version in versions
    }

    assert versions_by_number[1].id == document.id
    assert versions_by_number[1].status == (
        ClinicalDocumentStatus.SIGNED
    )

    assert versions_by_number[2].id == version_two.id
    assert versions_by_number[2].status == (
        ClinicalDocumentStatus.SIGNED
    )


def test_amend_document_allows_latest_signed_version(
    db,
    hospital,
):
    """
    The latest signed version of a Clinical Document may be amended.

    Scenario:

        v1 SIGNED
          ↓
        amend
          ↓
        v2 DRAFT

    Version 2 must be created successfully.
    """

    context, staff, encounter, document, service = create_document(
        db,
        hospital,
        hospital_number="PAT-CD-LATEST-002",
        staff_number="STF-CD-LATEST-002",
    )

    # ------------------------------------------------------------------
    # Sign version 1
    # ------------------------------------------------------------------

    service.sign_document(
        context=context,
        document_id=document.id,
        signed_by=staff.id,
    )

    # ------------------------------------------------------------------
    # Amend the latest version.
    # ------------------------------------------------------------------

    amended = service.amend_document(
        context=context,
        document_id=document.id,
        authored_by=staff.id,
        content={
            "presenting_complaints": [
                "New complaint",
            ],
            "history_of_presenting_complaints": (
                "Updated history."
            ),
        },
    )

    # ------------------------------------------------------------------
    # Verify new version.
    # ------------------------------------------------------------------

    assert amended.id != document.id
    assert amended.encounter_id == encounter.id
    assert amended.document_type == document.document_type
    assert amended.version == 2
    assert amended.status == ClinicalDocumentStatus.DRAFT
    assert amended.authored_by == staff.id
    assert amended.amended_from_id == document.id

    # ------------------------------------------------------------------
    # Verify original remains immutable.
    # ------------------------------------------------------------------

    assert document.version == 1
    assert document.status == ClinicalDocumentStatus.SIGNED

    # ------------------------------------------------------------------
    # Verify version history.
    # ------------------------------------------------------------------

    versions = service.list_versions(
        context=context,
        encounter_id=encounter.id,
        document_type=document.document_type,
    )

    assert len(versions) == 2

    versions_by_number = {
        version.version: version
        for version in versions
    }

    assert versions_by_number[1].id == document.id
    assert versions_by_number[2].id == amended.id

    assert versions_by_number[1].status == (
        ClinicalDocumentStatus.SIGNED
    )

    assert versions_by_number[2].status == (
        ClinicalDocumentStatus.DRAFT
    )


def test_create_draft_rejects_closed_encounter(
    db,
    hospital,
):
    """
    Clinical Documents cannot be created against a CLOSED Encounter.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-CLOSED-001",
        staff_number="STF-CD-CLOSED-001",
    )

    service = create_service(db)

    # ------------------------------------------------------------------
    # Close the Encounter.
    #
    # We are deliberately manipulating the test fixture state here.
    # The test is concerned with the ClinicalDocumentService invariant,
    # not with testing EncounterService.
    # ------------------------------------------------------------------

    encounter.status = EncounterStatus.CLOSED

    db.flush()

    # ------------------------------------------------------------------
    # Creating a Clinical Document must now fail.
    # ------------------------------------------------------------------

    with pytest.raises(
        EncounterClosedError,
    ):
        service.create_draft(
            context=context,
            encounter_id=encounter.id,
            document_type=ClinicalDocumentType.INITIAL_CLERKING,
            authored_by=staff.id,
            content={
                "presenting_complaints": [
                    "Fever",
                ],
                "history_of_presenting_complaints": (
                    "Patient reports fever."
                ),
            },
        )


def test_create_discharge_summary_requires_admitted_episode(
    db,
    hospital,
):
    """
    A Discharge Summary cannot be created unless the Episode
    has ADMITTED status.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-DISCHARGE-001",
        staff_number="STF-CD-DISCHARGE-001",
    )

    service = create_service(db)

    # ------------------------------------------------------------------
    # The helper creates an OPEN Episode.
    #
    # Therefore a Discharge Summary must be rejected.
    # ------------------------------------------------------------------

    with pytest.raises(
        EpisodeNotAdmittedError,
    ):
        service.create_draft(
            context=context,
            encounter_id=encounter.id,
            document_type=ClinicalDocumentType.DISCHARGE_SUMMARY,
            authored_by=staff.id,
            content={
                "discharge_diagnosis": "Acute febrile illness",
                "hospital_course": (
                    "Patient was managed with supportive treatment."
                ),
                "discharge_medications": [],
                "follow_up_plan": (
                    "Follow up in clinic."
                ),
            },
        )


def test_non_managing_doctor_cannot_sign_discharge_summary(
    db,
    hospital,
):
    """
    Only the Episode managing doctor may sign a Discharge Summary.
    """

    context, managing_doctor, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-DISCHARGE-002",
        staff_number="STF-CD-DISCHARGE-002",
    )

    service = create_service(db)

    # ------------------------------------------------------------------
    # Retrieve the Episode.
    # ------------------------------------------------------------------

    episode_repository = EpisodeRepository(db)

    episode = episode_repository.get_by_id(
        hospital_id=hospital.id,
        episode_id=encounter.episode_id,
    )

    assert episode is not None

    # ------------------------------------------------------------------
    # Put the Episode into the state required for a Discharge Summary.
    #
    # The test is specifically testing ClinicalDocumentService's
    # managing-doctor rule.
    # ------------------------------------------------------------------

    episode.status = EpisodeStatus.ADMITTED
    episode.managing_doctor_id = managing_doctor.id

    db.flush()

    # ------------------------------------------------------------------
    # Create the Discharge Summary.
    # ------------------------------------------------------------------

    discharge_summary = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.DISCHARGE_SUMMARY,
        authored_by=managing_doctor.id,
        content={
            "discharge_diagnosis": "Acute febrile illness",
            "hospital_course": (
                "Patient was managed with supportive treatment."
            ),
            "discharge_medications": [],
            "follow_up_plan": (
                "Follow up in clinic."
            ),
        },
    )

    # ------------------------------------------------------------------
    # Create another doctor from the same Hospital.
    # ------------------------------------------------------------------

    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    )

    other_doctor = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-CD-DISCHARGE-003",
            first_name="Other",
            last_name="Doctor",
            gender=Gender.MALE,
            date_of_birth=date(1986, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        )
    )

    db.flush()

    # ------------------------------------------------------------------
    # The non-managing doctor must not be able to sign.
    # ------------------------------------------------------------------

    with pytest.raises(
        NotManagingDoctorError,
    ):
        service.sign_document(
            context=context,
            document_id=discharge_summary.id,
            signed_by=other_doctor.id,
        )

    # ------------------------------------------------------------------
    # The document must remain a DRAFT.
    # ------------------------------------------------------------------

    db.refresh(discharge_summary)

    assert discharge_summary.status == (
        ClinicalDocumentStatus.DRAFT
    )


def test_managing_doctor_can_sign_discharge_summary(
    db,
    hospital,
):
    """
    The Episode managing doctor may sign a Discharge Summary.
    """

    context, managing_doctor, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-DISCHARGE-004",
        staff_number="STF-CD-DISCHARGE-004",
    )

    service = create_service(db)

    # ------------------------------------------------------------------
    # Prepare the Episode as admitted and assign its managing doctor.
    # ------------------------------------------------------------------

    episode_repository = EpisodeRepository(db)

    episode = episode_repository.get_by_id(
        hospital_id=hospital.id,
        episode_id=encounter.episode_id,
    )

    assert episode is not None

    episode.status = EpisodeStatus.ADMITTED
    episode.managing_doctor_id = managing_doctor.id

    db.flush()

    # ------------------------------------------------------------------
    # Create the Discharge Summary.
    # ------------------------------------------------------------------

    discharge_summary = service.create_draft(
        context=context,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.DISCHARGE_SUMMARY,
        authored_by=managing_doctor.id,
        content={
            "discharge_diagnosis": "Acute febrile illness",
            "hospital_course": (
                "Patient was managed with supportive treatment."
            ),
            "discharge_medications": [],
            "follow_up_plan": (
                "Follow up in clinic."
            ),
        },
    )

    # ------------------------------------------------------------------
    # Managing doctor signs successfully.
    # ------------------------------------------------------------------

    signed = service.sign_document(
        context=context,
        document_id=discharge_summary.id,
        signed_by=managing_doctor.id,
    )

    assert signed.status == (
        ClinicalDocumentStatus.SIGNED
    )

    assert signed.signed_by == managing_doctor.id
    assert signed.signed_at is not None