from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from app.core.context import RequestContext
from app.modules.clinical_documents.services.clinical_document_service import (
    ClinicalDocumentService,
)
from app.modules.diagnoses.enums import (
    DiagnosisCertainty,
    DiagnosisType,
)
from app.modules.diagnoses.exceptions import (
    ClinicalDiagnosisEncounterClosedError,
    ClinicalDiagnosisEncounterNotFoundError,
    ClinicalDiagnosisEpisodeCancelledError,
    ClinicalDiagnosisEpisodeClosedError,
    ClinicalDiagnosisEpisodeNotFoundError,
    ClinicalDiagnosisStaffNotFoundError,
)
from app.modules.diagnoses.repositories import (
    ClinicalDiagnosisRepository,
)
from app.modules.diagnoses.services import (
    ClinicalDiagnosisService,
)
from app.modules.terminology.repositories import TerminologyRepository
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import ClinicalEventService
from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount
from app.modules.staff.repository import StaffRepository


def create_diagnosis_service(db):
    return ClinicalDiagnosisService(
        repository=ClinicalDiagnosisRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        terminology_repository=TerminologyRepository(db),
    )


def test_create_diagnosis_creates_diagnosis_and_event(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, staff, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    from app.modules.terminology.enums import TerminologySystem
    from app.modules.terminology.models import TerminologyConcept

    terminology_code = f"TEST-I10-{uuid4().hex[:8]}"

    concept = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=terminology_code,
        display_name="Essential (primary) hypertension",
        release_version="2026 Jan",
        is_leaf=True,
        is_residual=False,
        active=True,
    )

    db.add(concept)
    db.commit()

    service = create_diagnosis_service(db)

    diagnosis = service.create_diagnosis(
        context=context,
        encounter_id=encounter.id,
        diagnosis_name="Essential hypertension",
        code_system="ICD-10-CM",
        code=terminology_code,
        diagnosis_type=DiagnosisType.FINAL,
        certainty=DiagnosisCertainty.CONFIRMED,
        onset_date=date(2026, 8, 1),
        notes="Persistent elevated blood pressure.",
    )

    assert diagnosis.id is not None
    assert diagnosis.encounter_id == encounter.id
    assert diagnosis.episode_id == encounter.episode_id
    assert diagnosis.diagnosis_name == (
        "Essential (primary) hypertension"
    )
    assert diagnosis.code_system == "ICD-10-CM"
    assert diagnosis.code == terminology_code
    assert diagnosis.diagnosis_type == DiagnosisType.FINAL
    assert diagnosis.certainty == DiagnosisCertainty.CONFIRMED
    assert diagnosis.onset_date == date(2026, 8, 1)
    assert diagnosis.diagnosed_by == staff.id
    assert diagnosis.diagnosed_at is not None

    from app.modules.events.models import ClinicalEvent

    events = (
        db.query(ClinicalEvent)
        .filter(
            ClinicalEvent.encounter_id == encounter.id,
            ClinicalEvent.event_type == EventType.DIAGNOSIS_RECORDED,
        )
        .all()
    )

    assert len(events) == 1
    assert events[0].performed_by == staff.id
    assert events[0].payload["clinical_diagnosis_id"] == str(diagnosis.id)
    assert events[0].payload["code"] == terminology_code


def test_create_diagnosis_rejects_missing_encounter(
    db,
    hospital,
):
    context = RequestContext(
        user_id=uuid4(),
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = create_diagnosis_service(db)

    with pytest.raises(ClinicalDiagnosisEncounterNotFoundError):
        service.create_diagnosis(
            context=context,
            encounter_id=uuid4(),
            diagnosis_name="Hypertension",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty=DiagnosisCertainty.SUSPECTED,
        )


def test_create_diagnosis_rejects_closed_encounter(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter
    from app.modules.encounter.models import EncounterStatus

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    encounter.status = EncounterStatus.CLOSED
    db.commit()

    service = create_diagnosis_service(db)

    with pytest.raises(ClinicalDiagnosisEncounterClosedError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Hypertension",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty=DiagnosisCertainty.SUSPECTED,
        )


def test_create_diagnosis_rejects_cancelled_episode(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter
    from app.modules.episode.models import EpisodeStatus

    context, _, episode, encounter = create_test_encounter(
        db,
        hospital,
    )

    episode.status = EpisodeStatus.CANCELLED
    db.commit()

    service = create_diagnosis_service(db)

    with pytest.raises(ClinicalDiagnosisEpisodeCancelledError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Hypertension",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty=DiagnosisCertainty.SUSPECTED,
        )


def test_create_diagnosis_rejects_closed_episode(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter
    from app.modules.episode.models import EpisodeStatus

    context, _, episode, encounter = create_test_encounter(
        db,
        hospital,
    )

    episode.status = EpisodeStatus.CLOSED
    db.commit()

    service = create_diagnosis_service(db)

    with pytest.raises(ClinicalDiagnosisEpisodeClosedError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Hypertension",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty=DiagnosisCertainty.SUSPECTED,
        )


def test_create_diagnosis_rejects_user_without_staff_profile(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    user = UserAccount(
        hospital_id=hospital.id,
        email=f"diagnosis-orphan-{uuid4()}@example.com",
        password_hash="test-password-hash",
        status=AccountStatus.ACTIVE,
        is_superuser=False,
    )

    db.add(user)
    db.commit()

    context = RequestContext(
        user_id=user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = create_diagnosis_service(db)

    with pytest.raises(ClinicalDiagnosisStaffNotFoundError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Hypertension",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty=DiagnosisCertainty.SUSPECTED,
        )


def test_create_diagnosis_accepts_valid_terminology_concept(
    db,
    hospital,
):
    from app.modules.terminology.enums import TerminologySystem
    from app.modules.terminology.models import TerminologyConcept

    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    concept = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=f"TEST-I10-{uuid4().hex[:8]}",
        display_name="Essential (primary) hypertension",
        release_version="2026 Jan",
        is_leaf=True,
        is_residual=False,
        active=True,
    )

    db.add(concept)
    db.commit()

    service = create_diagnosis_service(db)

    diagnosis = service.create_diagnosis(
        context=context,
        encounter_id=encounter.id,
        diagnosis_name="Whatever the client supplied",
        code_system="ICD-10-CM",
        code=concept.code,
        diagnosis_type=DiagnosisType.FINAL,
        certainty=DiagnosisCertainty.CONFIRMED,
    )

    assert diagnosis.code_system == "ICD-10-CM"
    assert diagnosis.code == concept.code
    assert diagnosis.diagnosis_name == concept.display_name


def test_create_diagnosis_rejects_unknown_terminology_code(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_diagnosis_service(db)

    with pytest.raises(ValueError, match="not found or is inactive"):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Essential hypertension",
            code_system="ICD-10-CM",
            code=f"UNKNOWN-{uuid4().hex[:8]}",
            diagnosis_type=DiagnosisType.FINAL,
            certainty=DiagnosisCertainty.CONFIRMED,
        )


def test_create_diagnosis_rejects_inactive_terminology_concept(
    db,
    hospital,
):
    from app.modules.terminology.enums import TerminologySystem
    from app.modules.terminology.models import TerminologyConcept

    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    concept = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=f"TEST-I10-{uuid4().hex[:8]}",
        display_name="Essential (primary) hypertension",
        release_version="2026 Jan",
        is_leaf=True,
        is_residual=False,
        active=False,
    )

    db.add(concept)
    db.commit()

    service = create_diagnosis_service(db)

    with pytest.raises(ValueError, match="not found or is inactive"):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Essential hypertension",
            code_system="ICD-10-CM",
            code=concept.code,
            diagnosis_type=DiagnosisType.FINAL,
            certainty=DiagnosisCertainty.CONFIRMED,
        )


def test_create_diagnosis_rejects_invalid_type(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_diagnosis_service(db)

    with pytest.raises(ValueError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Hypertension",
            diagnosis_type="INVALID",
            certainty=DiagnosisCertainty.SUSPECTED,
        )


def test_create_diagnosis_rejects_invalid_certainty(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_diagnosis_service(db)

    with pytest.raises(ValueError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="Hypertension",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty="INVALID",
        )


def test_create_diagnosis_rejects_blank_name(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_diagnosis_service(db)

    with pytest.raises(ValueError):
        service.create_diagnosis(
            context=context,
            encounter_id=encounter.id,
            diagnosis_name="   ",
            diagnosis_type=DiagnosisType.PROVISIONAL,
            certainty=DiagnosisCertainty.POSSIBLE,
        )


def test_list_encounter_diagnoses_returns_in_diagnosed_order(
    db,
    hospital,
):
    from tests.clinical_orders_test_service import create_test_encounter

    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    service = create_diagnosis_service(db)

    first = service.create_diagnosis(
        context=context,
        encounter_id=encounter.id,
        diagnosis_name="Headache",
        diagnosis_type=DiagnosisType.DIFFERENTIAL,
        certainty=DiagnosisCertainty.POSSIBLE,
    )

    second = service.create_diagnosis(
        context=context,
        encounter_id=encounter.id,
        diagnosis_name="Migraine",
        diagnosis_type=DiagnosisType.PROVISIONAL,
        certainty=DiagnosisCertainty.SUSPECTED,
    )

    diagnoses = service.list_encounter_diagnoses(
        context=context,
        encounter_id=encounter.id,
    )

    assert [item.id for item in diagnoses] == [
        first.id,
        second.id,
    ]
