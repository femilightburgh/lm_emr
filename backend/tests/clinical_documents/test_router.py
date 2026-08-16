"""
==============================================================================
LIGHTBURGH EMR

Clinical Document API Tests
==============================================================================

Tests the HTTP API for Clinical Documents.

Coverage
--------
• Create draft
• Retrieve document
• List encounter documents
• Sign document
• Signing creates Clinical Event
• Amend signed document
• Amendment does not create Event
• Sign amended document
• Second signing creates second Event
• Cross-hospital document access
• Invalid document lifecycle transitions
==============================================================================
"""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.context import RequestContext, get_request_context
from app.db.session import get_db
from app.main import app

from app.modules.clinical_documents.enums import ClinicalDocumentType

from app.modules.events.enums import EventType
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import (
    EpisodeService,
)

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
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
# Test Client
# ============================================================================


@pytest.fixture
def client(
    db: Session,
    hospital,
):
    def override_get_db():
        yield db

    def override_get_request_context():
        return RequestContext(
            user_id=uuid4(),
            hospital_id=hospital.id,
            permissions=frozenset(),
        )

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_request_context] = (
        override_get_request_context
    )

    yield TestClient(app)

    app.dependency_overrides.clear()


# ============================================================================
# Test Helpers
# ============================================================================


def create_test_encounter(
    db: Session,
    hospital,
    *,
    hospital_number: str,
    staff_number: str,
):
    """
    Create the Patient → Episode → Staff → Encounter chain required
    for Clinical Document API tests.
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
# Create
# ============================================================================


def test_create_clinical_document_endpoint(
    client,
    db,
    hospital,
):
    context, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-001",
        staff_number="API-CD-001",
    )

    response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "presenting_complaints": [
                    {
                        "complaint": "Fever",
                        "duration": "3 days",
                    },
                ],
                "history_of_presenting_complaint": (
                    "Fever started three days ago."
                ),
                "examination": {
                    "general": "Conscious and alert.",
                },
                "assessment": {
                    "working_diagnosis": "Malaria",
                    "differentials": [
                        "Typhoid fever",
                    ],
                },
            },
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["encounter_id"] == str(encounter.id)
    assert body["document_type"] == "INITIAL_CLERKING"
    assert body["status"] == "DRAFT"
    assert body["version"] == 1
    assert body["authored_by"] == str(staff.id)
    assert body["signed_at"] is None
    assert body["signed_by"] is None

    assert body["content"]["presenting_complaints"][0]["complaint"] == (
        "Fever"
    )


# ============================================================================
# Get
# ============================================================================


def test_get_clinical_document_endpoint(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-002",
        staff_number="API-CD-002",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Patient has fever."
                ),
            },
        },
    )

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/clinical-documents/{document_id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == document_id
    assert body["encounter_id"] == str(encounter.id)
    assert body["document_type"] == "INITIAL_CLERKING"
    assert body["status"] == "DRAFT"


# ============================================================================
# Encounter Documents
# ============================================================================


def test_list_encounter_documents_endpoint(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-003",
        staff_number="API-CD-003",
    )

    for history in (
        "First clinical document.",
        "Second clinical document.",
    ):
        response = client.post(
            "/api/v1/clinical-documents",
            json={
                "encounter_id": str(encounter.id),
                "document_type": "INITIAL_CLERKING",
                "authored_by": str(staff.id),
                "content": {
                    "history_of_presenting_complaint": history,
                },
            },
        )

        assert response.status_code == 201

    response = client.get(
        f"/api/v1/clinical-documents/encounters/{encounter.id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert all(
        document["encounter_id"] == str(encounter.id)
        for document in body
    )


# ============================================================================
# Sign
# ============================================================================


def test_sign_clinical_document_endpoint(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-004",
        staff_number="API-CD-004",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Patient has fever."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    signed_at = datetime(
        2026,
        8,
        16,
        10,
        0,
        tzinfo=timezone.utc,
    )

    response = client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
            "signed_at": signed_at.isoformat(),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "SIGNED"
    assert body["signed_by"] == str(staff.id)
    assert body["signed_at"] is not None


# ============================================================================
# Signing creates Event
# ============================================================================


def test_signing_document_creates_clinical_event(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-005",
        staff_number="API-CD-005",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Patient has fever."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    assert response.status_code == 200

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert len(events) == 1
    assert events[0].event_type == EventType.CLINICAL_NOTE_RECORDED
    assert events[0].payload["clinical_document_id"] == document_id
    assert events[0].payload["version"] == 1


# ============================================================================
# Amend
# ============================================================================


def test_amend_clinical_document_endpoint(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-006",
        staff_number="API-CD-006",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Original history."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    sign_response = client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    assert sign_response.status_code == 200

    amend_response = client.post(
        f"/api/v1/clinical-documents/{document_id}/amend",
        json={
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Amended history."
                ),
            },
        },
    )

    assert amend_response.status_code == 201

    body = amend_response.json()

    assert body["status"] == "DRAFT"
    assert body["version"] == 2
    assert body["amended_from_id"] == document_id
    assert body["signed_at"] is None
    assert body["signed_by"] is None
    assert body["content"]["history_of_presenting_complaint"] == (
        "Amended history."
    )


# ============================================================================
# Amendment does not create Event
# ============================================================================


def test_amendment_does_not_create_second_event(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-007",
        staff_number="API-CD-007",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Original history."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    amend_response = client.post(
        f"/api/v1/clinical-documents/{document_id}/amend",
        json={
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Amended history."
                ),
            },
        },
    )

    assert amend_response.status_code == 201

    event_repository = ClinicalEventRepository(db)

    events = event_repository.list_by_encounter(
        hospital_id=hospital.id,
        encounter_id=encounter.id,
    )

    assert len(events) == 1
    assert events[0].payload["version"] == 1


# ============================================================================
# Sign Amendment
# ============================================================================


def test_sign_amended_document_creates_second_event(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-008",
        staff_number="API-CD-008",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Original history."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    amend_response = client.post(
        f"/api/v1/clinical-documents/{document_id}/amend",
        json={
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Amended history."
                ),
            },
        },
    )

    amended_id = amend_response.json()["id"]

    response = client.post(
        f"/api/v1/clinical-documents/{amended_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    assert response.status_code == 200

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

    assert events[0].payload["version"] == 1
    assert events[1].payload["version"] == 2


# ============================================================================
# Invalid Lifecycle Transitions
# ============================================================================


def test_cannot_sign_already_signed_document(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-009",
        staff_number="API-CD-009",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Patient has fever."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    first_sign = client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    assert first_sign.status_code == 200

    second_sign = client.post(
        f"/api/v1/clinical-documents/{document_id}/sign",
        json={
            "signed_by": str(staff.id),
        },
    )

    assert second_sign.status_code == 409


def test_cannot_amend_draft_document(
    client,
    db,
    hospital,
):
    _, staff, encounter = create_test_encounter(
        db,
        hospital,
        hospital_number="API-CD-010",
        staff_number="API-CD-010",
    )

    create_response = client.post(
        "/api/v1/clinical-documents",
        json={
            "encounter_id": str(encounter.id),
            "document_type": "INITIAL_CLERKING",
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Patient has fever."
                ),
            },
        },
    )

    document_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/clinical-documents/{document_id}/amend",
        json={
            "authored_by": str(staff.id),
            "content": {
                "history_of_presenting_complaint": (
                    "Attempted amendment."
                ),
            },
        },
    )

    assert response.status_code == 409