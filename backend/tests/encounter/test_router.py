import pytest

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.context import (
    RequestContext,
    get_request_context,
)
from app.db.session import get_db
from app.main import app

from app.modules.encounter.models import EncounterStatus
from app.modules.identity.auth_service import AuthService
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.token_service import TokenService
from app.modules.identity.user_service import UserService

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

from tests.clinical_orders.test_router import (
    authenticate,
    auth_headers,
    create_hospital,
    create_user,
)
from app.modules.encounter.repositories.encounter_repository import EncounterRepository
from app.modules.encounter.services.encounter_service import EncounterService


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



def create_test_user(
    db,
    *,
    hospital,
    email: str,
    role_name: str = "Doctor",
):
    user_service = UserService(
        repository=IdentityRepository(db),
    )

    user = user_service.create_user(
        hospital_code=hospital.code,
        email=email,
        password="password123",
        role_name=role_name,
    )

    repository = IdentityRepository(db)
    repository.save()
    repository.refresh(user)

    return user


def authenticate_test_user(
    db,
    *,
    hospital,
    email: str,
) -> str:
    auth_service = AuthService(
        repository=IdentityRepository(db),
        token_service=TokenService(),
    )

    response = auth_service.login(
        hospital_code=hospital.code,
        email=email,
        password="password123",
    )

    return response.access_token



def test_list_doctor_queue_endpoint(
    client,
    db,
):
    hospital = create_hospital(db)

    user = create_user(
        db,
        hospital=hospital,
        email=f"doctor-{uuid4()}@example.com",
        role_name="Doctor",
    )

    # Resolve the UserAccount to a Staff profile.
    staff_service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = staff_service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"API-QUEUE-{uuid4().hex[:8]}",
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

    # Build an Episode + Encounter owned by this doctor.
    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
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

    token = authenticate(
        db,
        hospital=hospital,
        email=user.email,
    )

    app.dependency_overrides[get_request_context] = (
        lambda: RequestContext(
            user_id=user.id,
            hospital_id=hospital.id,
            permissions=frozenset(),
        )
    )

    response = client.get(
        "/api/v1/encounters/queue/doctor",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["id"] for item in body] == [
        str(encounter.id),
    ]
    assert body[0]["staff_id"] == str(staff.id)
    assert body[0]["status"] == "OPEN"


# ============================================================================
# Create Encounter
# ============================================================================


def test_create_encounter_endpoint(
    client,
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
            hospital_number="API-PAT-001",
            first_name="John",
            last_name="Doe",
            sex="Male",
            date_of_birth=date(1990, 1, 15),
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
            staff_number="API-ENC-001",
            first_name="Jane",
            last_name="Smith",
            gender=Gender.FEMALE,
            date_of_birth=date(1988, 5, 10),
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

    response = client.post(
        "/api/v1/encounters",
        json={
            "episode_id": str(episode.id),
            "staff_id": str(staff.id),
            "title": "Doctor Consultation",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["episode_id"] == str(episode.id)
    assert body["staff_id"] == str(staff.id)
    assert body["title"] == "Doctor Consultation"
    assert body["status"] == "OPEN"
    assert body["started_at"] is not None
    assert body["ended_at"] is None
    assert "id" in body


# ============================================================================
# Get Encounter
# ============================================================================


def test_get_encounter_endpoint(
    client,
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
            hospital_number="API-PAT-002",
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
            staff_number="API-ENC-002",
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

    create_response = client.post(
        "/api/v1/encounters",
        json={
            "episode_id": str(episode.id),
            "staff_id": str(staff.id),
            "title": "Nurse Consultation",
        },
    )

    assert create_response.status_code == 201

    encounter_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/encounters/{encounter_id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == encounter_id
    assert body["episode_id"] == str(episode.id)
    assert body["staff_id"] == str(staff.id)
    assert body["title"] == "Nurse Consultation"
    assert body["status"] == "OPEN"
    assert body["ended_at"] is None


# ============================================================================
# Close Encounter
# ============================================================================


def test_close_encounter_endpoint(
    client,
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
            hospital_number="API-PAT-003",
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
            staff_number="API-ENC-003",
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

    create_response = client.post(
        "/api/v1/encounters",
        json={
            "episode_id": str(episode.id),
            "staff_id": str(staff.id),
            "title": "Doctor Consultation",
        },
    )

    assert create_response.status_code == 201

    encounter_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/encounters/{encounter_id}/close",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == encounter_id
    assert body["status"] == "CLOSED"
    assert body["ended_at"] is not None


# ============================================================================
# Close Encounter Twice
# ============================================================================


def test_close_encounter_twice_returns_conflict(
    client,
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
            hospital_number="API-PAT-004",
            first_name="Robert",
            last_name="Williams",
            sex="Male",
            date_of_birth=date(1985, 9, 5),
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
            staff_number="API-ENC-004",
            first_name="Sarah",
            last_name="Johnson",
            gender=Gender.FEMALE,
            date_of_birth=date(1991, 7, 12),
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
        title="Follow-up Consultation",
    )

    create_response = client.post(
        "/api/v1/encounters",
        json={
            "episode_id": str(episode.id),
            "staff_id": str(staff.id),
            "title": "Nurse Follow-up",
        },
    )

    assert create_response.status_code == 201

    encounter_id = create_response.json()["id"]

    first_close = client.post(
        f"/api/v1/encounters/{encounter_id}/close",
    )

    assert first_close.status_code == 200

    second_close = client.post(
        f"/api/v1/encounters/{encounter_id}/close",
    )

    assert second_close.status_code == 409

    body = second_close.json()

    assert body["detail"] == "Encounter is already closed."