"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Repository Tests
==============================================================================

Tests persistence and hospital-tenancy behavior for Clinical Documents.

Business rules such as signing and amendment workflows are tested at the
service layer.

==============================================================================
"""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.context import RequestContext

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)
from app.modules.clinical_documents.models import ClinicalDocument
from app.modules.clinical_documents.repositories import (
    ClinicalDocumentRepository,
)

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
    Create the minimum Patient → Episode → Staff → Encounter hierarchy
    required by Clinical Document repository tests.
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
            first_name="Document",
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
            staff_number=staff_number,
            first_name="Document",
            last_name="Clinician",
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


def create_test_document(
    db,
    *,
    encounter_id,
    staff_id,
    version: int = 1,
    status: ClinicalDocumentStatus = ClinicalDocumentStatus.DRAFT,
    amended_from_id=None,
):
    """
    Create and persist a Clinical Document directly through the repository.
    """

    repository = ClinicalDocumentRepository(db)

    document = ClinicalDocument(
        encounter_id=encounter_id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        status=status,
        version=version,
        content={
            "history": {
                "presenting_complaints": [
                    "Fever",
                ],
                "history_of_presenting_complaint": (
                    "Patient reports fever for three days."
                ),
            },
            "examination": {
                "general": (
                    "Patient is conscious, alert and mildly febrile."
                ),
            },
        },
        authored_by=staff_id,
        amended_from_id=amended_from_id,
    )

    repository.create(
        document=document,
    )

    repository.save()
    repository.refresh(document)

    return document


# ============================================================================
# Create
# ============================================================================


def test_create_document_persists_document(
    db,
    hospital,
):
    """
    A Clinical Document should be persisted successfully.
    """

    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-001",
        staff_number="STF-CD-001",
    )

    document = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
    )

    assert document.id is not None
    assert document.encounter_id == encounter.id
    assert document.document_type == ClinicalDocumentType.INITIAL_CLERKING
    assert document.status == ClinicalDocumentStatus.DRAFT
    assert document.version == 1
    assert document.authored_by == staff.id
    assert document.amended_from_id is None

    assert document.content["history"]["presenting_complaints"] == [
        "Fever",
    ]


# ============================================================================
# Version Uniqueness
# ============================================================================


def test_create_document_rejects_duplicate_version_for_same_encounter_and_type(
    db,
    hospital,
):
    """
    The database must reject two Clinical Documents with the same:

        encounter_id
        document_type
        version

    Different versions of the same document type are valid.

    The uniqueness constraint protects the version history from
    containing two competing versions with the same version number.
    """

    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-UNIQUE-001",
        staff_number="STF-CD-UNIQUE-001",
    )

    first_document = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=1,
    )

    repository = ClinicalDocumentRepository(db)

    duplicate_document = ClinicalDocument(
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        status=ClinicalDocumentStatus.DRAFT,
        version=1,
        content={
            "history": {
                "presenting_complaints": [
                    "Cough",
                ],
            },
        },
        authored_by=staff.id,
    )

    repository.create(
        document=duplicate_document,
    )

    with pytest.raises(IntegrityError):
        repository.save()

    # --------------------------------------------------------------
    # The failed transaction must be rolled back before the Session
    # can be used again.
    # --------------------------------------------------------------

    db.rollback()

    documents = repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert len(documents) == 1
    assert documents[0].id == first_document.id
    assert documents[0].version == 1


def test_create_document_allows_different_versions_for_same_encounter_and_type(
    db,
    hospital,
):
    """
    The same Encounter and Document Type may have multiple versions,
    provided every version number is unique.
    """

    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-VERSION-001",
        staff_number="STF-CD-VERSION-001",
    )

    version_one = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=1,
    )

    version_two = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=2,
        amended_from_id=version_one.id,
    )

    version_three = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=3,
        amended_from_id=version_two.id,
    )

    assert version_one.version == 1
    assert version_two.version == 2
    assert version_three.version == 3

    assert version_two.amended_from_id == version_one.id
    assert version_three.amended_from_id == version_two.id


# ============================================================================
# Retrieve By ID
# ============================================================================


def test_get_by_id_returns_document(
    db,
    hospital,
):
    """
    A Clinical Document should be retrievable by ID within its Hospital.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-002",
        staff_number="STF-CD-002",
    )

    original = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
    )

    repository = ClinicalDocumentRepository(db)

    document = repository.get_by_id(
        hospital_id=context.hospital_id,
        document_id=original.id,
    )

    assert document is not None
    assert document.id == original.id


# ============================================================================
# Missing Document
# ============================================================================


def test_get_by_id_returns_none_for_missing_document(
    db,
    hospital,
):
    """
    An unknown Clinical Document ID should return None.
    """

    repository = ClinicalDocumentRepository(db)

    document = repository.get_by_id(
        hospital_id=hospital.id,
        document_id=uuid4(),
    )

    assert document is None


# ============================================================================
# Hospital Tenancy
# ============================================================================


def test_get_by_id_does_not_return_another_hospital_document(
    db,
    hospital,
    hospital_two,
):
    """
    A Hospital must not retrieve another Hospital's Clinical Document.
    """

    context_one, staff_one, encounter_one = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-H1-001",
        staff_number="STF-CD-H1-001",
    )

    context_two, staff_two, encounter_two = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-CD-H2-001",
        staff_number="STF-CD-H2-001",
    )

    document_two = create_test_document(
        db,
        encounter_id=encounter_two.id,
        staff_id=staff_two.id,
    )

    repository = ClinicalDocumentRepository(db)

    result = repository.get_by_id(
        hospital_id=context_one.hospital_id,
        document_id=document_two.id,
    )

    assert result is None

    # Confirm the owning Hospital can retrieve it.
    result = repository.get_by_id(
        hospital_id=context_two.hospital_id,
        document_id=document_two.id,
    )

    assert result is not None
    assert result.id == document_two.id


# ============================================================================
# Encounter Documents
# ============================================================================


def test_list_by_encounter_returns_documents(
    db,
    hospital,
):
    """
    Documents belonging to an Encounter should be returned.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-003",
        staff_number="STF-CD-003",
    )

    document_one = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=1,
    )

    document_two = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=2,
        amended_from_id=document_one.id,
    )

    repository = ClinicalDocumentRepository(db)

    documents = repository.list_by_encounter(
        hospital_id=context.hospital_id,
        encounter_id=encounter.id,
    )

    document_ids = {document.id for document in documents}

    assert document_one.id in document_ids
    assert document_two.id in document_ids


# ============================================================================
# Encounter Tenancy
# ============================================================================


def test_list_by_encounter_does_not_return_another_hospital_documents(
    db,
    hospital,
    hospital_two,
):
    """
    Encounter document listing must respect Hospital tenancy.
    """

    context_one, _, encounter_one = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-H1-002",
        staff_number="STF-CD-H1-002",
    )

    _, staff_two, encounter_two = create_test_encounter(
        db,
        hospital_two,
        hospital_number="PAT-CD-H2-002",
        staff_number="STF-CD-H2-002",
    )

    document_two = create_test_document(
        db,
        encounter_id=encounter_two.id,
        staff_id=staff_two.id,
    )

    repository = ClinicalDocumentRepository(db)

    documents = repository.list_by_encounter(
        hospital_id=context_one.hospital_id,
        encounter_id=encounter_two.id,
    )

    assert documents == []
    assert document_two.id not in {
        document.id for document in documents
    }


# ============================================================================
# Version History
# ============================================================================


def test_list_versions_returns_versions_in_order(
    db,
    hospital,
):
    """
    Document versions should be returned from oldest to newest.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-004",
        staff_number="STF-CD-004",
    )

    version_one = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=1,
    )

    version_two = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=2,
        amended_from_id=version_one.id,
    )

    version_three = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=3,
        amended_from_id=version_two.id,
    )

    repository = ClinicalDocumentRepository(db)

    versions = repository.list_versions(
        hospital_id=context.hospital_id,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
    )

    assert [document.version for document in versions] == [
        1,
        2,
        3,
    ]

    assert versions[0].id == version_one.id
    assert versions[1].id == version_two.id
    assert versions[2].id == version_three.id


# ============================================================================
# Amendment Relationship
# ============================================================================


def test_document_version_points_to_previous_version(
    db,
    hospital,
):
    """
    An amended document version should point to the version it replaces.
    """

    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-005",
        staff_number="STF-CD-005",
    )

    version_one = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=1,
        status=ClinicalDocumentStatus.SIGNED,
    )

    version_two = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=2,
        status=ClinicalDocumentStatus.DRAFT,
        amended_from_id=version_one.id,
    )

    assert version_two.amended_from_id == version_one.id
    assert version_two.amended_from.id == version_one.id
    assert version_two.version == 2


# ============================================================================
# Document Type Filtering
# ============================================================================


def test_list_versions_only_returns_requested_document_type(
    db,
    hospital,
):
    """
    Version history should only contain the requested document type.
    """

    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="PAT-CD-006",
        staff_number="STF-CD-006",
    )

    clerking = create_test_document(
        db,
        encounter_id=encounter.id,
        staff_id=staff.id,
        version=1,
    )

    repository = ClinicalDocumentRepository(db)

    other_document = ClinicalDocument(
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.PROGRESS_NOTE,
        status=ClinicalDocumentStatus.DRAFT,
        version=1,
        content={
            "note": "Patient reviewed.",
        },
        authored_by=staff.id,
    )

    repository.create(
        document=other_document,
    )

    repository.save()
    repository.refresh(other_document)

    versions = repository.list_versions(
        hospital_id=context.hospital_id,
        encounter_id=encounter.id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
    )

    assert len(versions) == 1
    assert versions[0].id == clerking.id
    assert versions[0].document_type == (
        ClinicalDocumentType.INITIAL_CLERKING
    )