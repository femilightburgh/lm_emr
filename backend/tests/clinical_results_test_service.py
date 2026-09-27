"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Service Tests
==============================================================================
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.context import RequestContext
from app.bootstrap.laboratory import (
    bootstrap_laboratory_tests,
)
from app.modules.clinical_orders.enums import ClinicalOrderStatus
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    PrescriptionRepository,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
)
from app.modules.diagnostics.repositories.diagnostic_repository import (
    DiagnosticRepository,
)
from app.modules.laboratory.repositories import (
    LaboratoryTestRepository,
)
from app.modules.clinical_results.enums import (
    ClinicalResultStatus,
    ClinicalResultType,
)
from app.modules.clinical_results.exceptions import (
    ClinicalResultDuplicateAnalyteError,
    ClinicalResultInvalidValueError,
    ClinicalResultOrderAlreadyCompletedError,
    ClinicalResultUnknownAnalyteError,
    ClinicalResultOrderCancelledError,
    ClinicalResultUnsupportedOrderTypeError,
)
from app.modules.clinical_results.repositories import (
    ClinicalResultRepository,
)
from app.modules.clinical_results.services import (
    ClinicalResultService,
)
from app.modules.clinical_orders.enums import ClinicalOrderType
from app.modules.laboratory.models import LaboratoryTest
from app.modules.encounter.models import EncounterStatus
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)
from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.repositories.episode_disposition_repository import (
    EpisodeDispositionRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import EpisodeService
from app.modules.events.enums import EventType
from app.modules.events.models import ClinicalEvent
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.identity.enums import AccountStatus
from app.modules.identity.models import UserAccount
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


def create_test_encounter(
    db,
    hospital,
):
    user = UserAccount(
        hospital_id=hospital.id,
        email=f"result-{uuid4()}@example.com",
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

    bootstrap_laboratory_tests(
        db,
        hospital_id=hospital.id,
    )

    patient = PatientService(
        repository=PatientRepository(db),
    ).create_patient(
        context=context,
        request=CreatePatientRequest(
            hospital_id=hospital.id,
            hospital_number=f"PAT-RESULT-{uuid4().hex[:8]}",
            first_name="Result",
            last_name="Patient",
            sex="Male",
            date_of_birth=datetime(1990, 1, 1).date(),
        ),
    )

    staff = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
    ).create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number=f"STF-RESULT-{uuid4().hex[:8]}",
            first_name="Result",
            last_name="Clinician",
            gender=Gender.MALE,
            date_of_birth=datetime(1985, 1, 1).date(),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=datetime(2026, 1, 1).date(),
        )
    )

    staff.user_account_id = user.id
    db.flush()

    episode_repository = EpisodeRepository(db)

    episode = EpisodeService(
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
    ).create_episode(
        context=context,
        patient_id=patient.id,
        title="Clinical Result Test Episode",
    )

    encounter = EncounterService(
        repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
    ).create_encounter(
        context=context,
        episode_id=episode.id,
        staff_id=staff.id,
        title="Doctor Consultation",
    )

    return context, staff, episode, encounter


def create_order_service(db):
    return ClinicalOrderService(
        repository=ClinicalOrderRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        encounter_repository=EncounterRepository(db),
        episode_repository=EpisodeRepository(db),
        staff_repository=StaffRepository(db),
        prescription_repository=PrescriptionRepository(db),
        laboratory_test_repository=LaboratoryTestRepository(db),
        diagnostic_repository=DiagnosticRepository(db),
    )


def create_laboratory_order(
    db,
    *,
    context,
    encounter_id,
    laboratory_test_id,
):
    order = create_order_service(db).create_order(
        context=context,
        encounter_id=encounter_id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={},
        items=[
            {
                "laboratory_test_id": laboratory_test_id,
            },
        ],
    )

    # Result-service tests begin at the point where the laboratory
    # investigation is actively being processed.
    order.items[0].status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    return order


def get_laboratory_test(
    db,
    *,
    hospital_id,
    code,
):
    return (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital_id,
            LaboratoryTest.code == code,
        )
        .one()
    )


def create_laboratory_order_by_code(
    db,
    *,
    context,
    encounter_id,
    code,
):
    laboratory_test = get_laboratory_test(
        db,
        hospital_id=context.hospital_id,
        code=code,
    )

    return create_laboratory_order(
        db,
        context=context,
        encounter_id=encounter_id,
        laboratory_test_id=laboratory_test.id,
    )


def create_result_service(db):
    return ClinicalResultService(
        repository=ClinicalResultRepository(db),
        clinical_order_repository=ClinicalOrderRepository(db),
        episode_repository=EpisodeRepository(db),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(db),
        ),
        staff_repository=StaffRepository(db),
    )


def test_record_laboratory_result_completes_order_and_creates_event(
    db,
    hospital,
):
    context, staff, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order_service = create_order_service(db)

    laboratory_test = get_laboratory_test(
        db,
        hospital_id=hospital.id,
        code="CBC",
    )

    order = create_laboratory_order(
        db,
        context=context,
        encounter_id=encounter.id,
        laboratory_test_id=laboratory_test.id,
    )

    order_item = order.items[0]

    result_service = create_result_service(db)

    result = result_service.record_result(
        context=context,
        order_id=order.id,
        order_item_id=order_item.id,
        result_type=ClinicalResultType.LABORATORY,
        result_data={
            "hemoglobin": 13.2,
            "white_cell_count": 6.8,
        },
    )

    db.refresh(order)
    db.refresh(encounter)

    assert result.id is not None
    assert result.order_id == order.id
    assert result.order_item_id == order_item.id
    assert result.recorded_by == staff.id
    assert result.result_type == ClinicalResultType.LABORATORY
    assert result.result_data["hemoglobin"] == 13.2

    assert order.status == ClinicalOrderStatus.COMPLETED
    assert order.completed_at is not None

    assert encounter.status == EncounterStatus.OPEN

    event = db.query(ClinicalEvent).filter(
        ClinicalEvent.encounter_id == encounter.id,
        ClinicalEvent.event_type == EventType.RESULT_RECORDED,
    ).one()

    assert event.performed_by == staff.id
    assert event.payload["clinical_order_id"] == str(order.id)
    assert event.payload["clinical_result_id"] == str(result.id)
    assert event.payload["result_type"] == "LABORATORY"


def test_record_result_rejects_medication_order(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_order_service(db).create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.MEDICATION,
        priority="ROUTINE",
        details={
            "medication_id": "MED-001",
            "dose": "500 mg",
        },
    )

    with pytest.raises(
        ClinicalResultUnsupportedOrderTypeError,
    ):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            result_type=ClinicalResultType.LABORATORY,
            result_data={
                "value": 1,
            },
        )


def test_record_result_rejects_cancelled_order(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.CANCELLED
    db.commit()

    with pytest.raises(
        ClinicalResultOrderCancelledError,
    ):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            result_data={
                "hemoglobin": 13.2,
            },
        )


def test_record_result_rejects_completed_order(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.COMPLETED
    db.commit()

    with pytest.raises(
        ClinicalResultOrderAlreadyCompletedError,
    ):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            result_data={
                "hemoglobin": 13.2,
            },
        )


def test_record_result_rejects_mismatched_result_type(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_order_service(db).create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.RADIOLOGY,
        priority="ROUTINE",
        details={
            "study_code": "CXR",
        },
    )

    with pytest.raises(
        ClinicalResultUnsupportedOrderTypeError,
    ):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            result_type=ClinicalResultType.LABORATORY,
            result_data={
                "finding": "Normal",
            },
        )


def test_last_investigation_result_moves_episode_to_awaiting_review(
    db,
    hospital,
):
    context, staff, episode, encounter = create_test_encounter(
        db,
        hospital,
    )

    episode.managing_doctor_id = staff.id
    db.commit()

    order_service = create_order_service(db)
    result_service = create_result_service(db)

    first = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    first_item = first.items[0]

    second = order_service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.RADIOLOGY,
        priority="ROUTINE",
        details={
            "study_code": "CXR",
        },
    )

    episode.flow_status = (
        __import__(
            "app.modules.episode.models",
            fromlist=["EpisodeFlowStatus"],
        ).EpisodeFlowStatus.AWAITING_INVESTIGATIONS
    )
    db.commit()

    result_service.record_result(
        context=context,
        order_id=first.id,
        order_item_id=first.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        result_data={
            "hemoglobin": 13.2,
        },
    )

    db.refresh(episode)

    assert episode.flow_status.value == "AWAITING_INVESTIGATIONS"

    result_service.record_result(
        context=context,
        order_id=second.id,
        result_type=ClinicalResultType.RADIOLOGY,
        result_data={
            "impression": "No acute cardiopulmonary abnormality.",
        },
    )

    db.refresh(episode)

    assert episode.flow_status.value == "AWAITING_REVIEW"


def test_record_structured_laboratory_values(
    db,
    hospital,
):
    from app.modules.laboratory.models import LaboratoryTest

    context, staff, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order_service = create_order_service(db)

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order_item = order.items[0]

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    analytes = {
        analyte.code: analyte
        for analyte in laboratory_test.analytes
    }

    result_service = create_result_service(db)

    result = result_service.record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        values=[
            {
                "analyte_id": analytes["hemoglobin"].id,
                "value_numeric": 11.2,
                "abnormal_flag": "LOW",
            },
            {
                "analyte_id": analytes["white_cell_count"].id,
                "value_numeric": 8.4,
            },
        ],
        specimen="EDTA blood",
        interpretation="Mild anaemia.",
    )

    db.refresh(result)

    assert result.specimen == "EDTA blood"
    assert result.interpretation == "Mild anaemia."
    assert len(result.values) == 2

    saved = {
        value.analyte.code: value
        for value in result.values
    }

    assert saved["hemoglobin"].value_numeric == 11.2
    assert saved["hemoglobin"].abnormal_flag == "LOW"
    assert saved["white_cell_count"].value_numeric == 8.4



def test_record_custom_laboratory_result(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        values=[
            {
                "custom_analyte_name": "Reticulocyte Count",
                "custom_analyte_code": "RETIC-CUSTOM",
                "custom_unit": "%",
                "custom_reference_low": 0.5,
                "custom_reference_high": 2.5,
                "custom_reference_text": "0.5-2.5%",
                "value_numeric": 3.1,
                "abnormal_flag": "HIGH",
                "comment": "Manual custom analyte.",
            },
        ],
    )

    db.refresh(result)

    assert len(result.values) == 1

    value = result.values[0]

    assert value.analyte_id is None
    assert value.custom_analyte_name == "Reticulocyte Count"
    assert value.custom_analyte_code == "RETIC-CUSTOM"
    assert value.custom_unit == "%"
    assert value.custom_reference_low == 0.5
    assert value.custom_reference_high == 2.5
    assert value.custom_reference_text == "0.5-2.5%"
    assert value.value_numeric == 3.1
    assert value.abnormal_flag == "HIGH"

    assert value.analyte_name == "Reticulocyte Count"
    assert value.analyte_code == "RETIC-CUSTOM"
    assert value.unit == "%"
    assert value.reference_low == 0.5
    assert value.reference_high == 2.5
    assert value.reference_text == "0.5-2.5%"


def test_record_result_rejects_value_with_catalogue_and_custom_analyte(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    laboratory_test = get_laboratory_test(
        db,
        hospital_id=hospital.id,
        code="CBC",
    )

    hemoglobin = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "hemoglobin"
    )

    with pytest.raises(ClinicalResultInvalidValueError):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "analyte_id": hemoglobin.id,
                    "custom_analyte_name": "Custom Haemoglobin",
                    "value_numeric": 13.0,
                },
            ],
        )


def test_record_result_rejects_value_without_analyte(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    with pytest.raises(ClinicalResultInvalidValueError):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "value_numeric": 13.0,
                },
            ],
        )


def test_record_result_rejects_invalid_custom_reference_range(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    with pytest.raises(ClinicalResultInvalidValueError):
        create_result_service(db).record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "custom_analyte_name": "Custom Test",
                    "custom_reference_low": 10,
                    "custom_reference_high": 5,
                    "value_numeric": 7,
                },
            ],
        )


def test_catalogue_laboratory_result_still_uses_analyte_metadata(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    laboratory_test = get_laboratory_test(
        db,
        hospital_id=hospital.id,
        code="CBC",
    )

    hemoglobin = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "hemoglobin"
    )

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        values=[
            {
                "analyte_id": hemoglobin.id,
                "value_numeric": 13.2,
            },
        ],
    )

    value = result.values[0]

    assert value.analyte_id == hemoglobin.id
    assert value.custom_analyte_name is None
    assert value.analyte_name == hemoglobin.name
    assert value.analyte_code == hemoglobin.code
    assert value.unit == hemoglobin.unit

def test_record_result_rejects_unknown_laboratory_analyte(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order_service = create_order_service(db)

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order_item = order.items[0]

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "EUCR",
        )
        .one()
    )

    sodium = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "sodium"
    )

    result_service = create_result_service(db)

    with pytest.raises(
        ClinicalResultUnknownAnalyteError,
    ):
        result_service.record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "analyte_id": sodium.id,
                    "value_numeric": 140,
                },
            ],
        )


def test_record_result_rejects_invalid_laboratory_value_type(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order_service = create_order_service(db)

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order_item = order.items[0]

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    hemoglobin = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "hemoglobin"
    )

    result_service = create_result_service(db)

    with pytest.raises(
        ClinicalResultInvalidValueError,
    ):
        result_service.record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "analyte_id": hemoglobin.id,
                    "value_text": "eleven",
                },
            ],
        )


def test_record_result_rejects_duplicate_analyte(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    hemoglobin = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "hemoglobin"
    )

    result_service = create_result_service(db)

    with pytest.raises(
        ClinicalResultDuplicateAnalyteError,
    ):
        result_service.record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "analyte_id": hemoglobin.id,
                    "value_numeric": 11.2,
                },
                {
                    "analyte_id": hemoglobin.id,
                    "value_numeric": 11.4,
                },
            ],
        )


def test_record_result_rejects_invalid_coded_value(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="MALARIA",
    )

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "MALARIA",
        )
        .one()
    )

    parasite_detected = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "parasite_detected"
    )

    result_service = create_result_service(db)

    with pytest.raises(
        ClinicalResultInvalidValueError,
    ):
        result_service.record_result(
            context=context,
            order_id=order.id,
            order_item_id=order.items[0].id,
            result_type=ClinicalResultType.LABORATORY,
            values=[
                {
                    "analyte_id": parasite_detected.id,
                    "value_code": "Unknown",
                },
            ],
        )


def test_record_result_accepts_valid_coded_value(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="MALARIA",
    )

    laboratory_test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "MALARIA",
        )
        .one()
    )

    parasite_detected = next(
        analyte
        for analyte in laboratory_test.analytes
        if analyte.code == "parasite_detected"
    )

    result_service = create_result_service(db)

    result = result_service.record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        values=[
            {
                "analyte_id": parasite_detected.id,
                "value_code": "Positive",
            },
        ],
    )

    assert len(result.values) == 1
    assert result.values[0].value_code == "Positive"


def test_record_draft_result_does_not_complete_order(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.DRAFT,
        result_data={
            "hemoglobin": 13.2,
        },
    )

    db.refresh(order)
    db.refresh(result)

    assert result.status == ClinicalResultStatus.DRAFT
    assert order.status == ClinicalOrderStatus.IN_PROGRESS
    assert order.completed_at is None


def test_finalize_result_completes_only_completed_group_item(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order_service = create_order_service(db)

    laboratory_tests = [
        get_laboratory_test(
            db,
            hospital_id=hospital.id,
            code=code,
        )
        for code in ("CBC", "EUCR", "LFT")
    ]

    order = order_service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={},
        items=[
            {
                "laboratory_test_id": laboratory_test.id,
            }
            for laboratory_test in laboratory_tests
        ],
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS

    cbc_item = order.items[0]
    eucr_item = order.items[1]
    lft_item = order.items[2]

    cbc_item.status = ClinicalOrderStatus.IN_PROGRESS

    db.commit()

    cbc_test = laboratory_tests[0]
    hemoglobin = next(
        analyte
        for analyte in cbc_test.analytes
        if analyte.code == "hemoglobin"
    )

    result_service = create_result_service(db)

    result = result_service.record_result(
        context=context,
        order_id=order.id,
        order_item_id=cbc_item.id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.DRAFT,
        values=[
            {
                "analyte_id": hemoglobin.id,
                "value_numeric": 13.2,
            },
        ],
    )

    db.refresh(order)
    assert result.status == ClinicalResultStatus.DRAFT
    assert order.status == ClinicalOrderStatus.IN_PROGRESS

    result = result_service.finalize_result(
        context=context,
        result_id=result.id,
    )

    db.refresh(order)
    db.refresh(cbc_item)
    db.refresh(eucr_item)
    db.refresh(lft_item)
    db.refresh(result)

    assert result.status == ClinicalResultStatus.FINAL
    assert cbc_item.status == ClinicalOrderStatus.COMPLETED
    assert eucr_item.status == ClinicalOrderStatus.REQUESTED
    assert lft_item.status == ClinicalOrderStatus.REQUESTED

    assert order.status == ClinicalOrderStatus.IN_PROGRESS
    assert order.completed_at is None


def test_record_final_result_completes_only_completed_group_item(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order_service = create_order_service(db)

    laboratory_tests = [
        get_laboratory_test(
            db,
            hospital_id=hospital.id,
            code=code,
        )
        for code in ("CBC", "EUCR", "LFT")
    ]

    order = order_service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={},
        items=[
            {
                "laboratory_test_id": laboratory_test.id,
            }
            for laboratory_test in laboratory_tests
        ],
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS

    cbc_item = order.items[0]
    eucr_item = order.items[1]
    lft_item = order.items[2]

    cbc_item.status = ClinicalOrderStatus.IN_PROGRESS

    db.commit()

    cbc_test = laboratory_tests[0]
    hemoglobin = next(
        analyte
        for analyte in cbc_test.analytes
        if analyte.code == "hemoglobin"
    )

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=cbc_item.id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.FINAL,
        values=[
            {
                "analyte_id": hemoglobin.id,
                "value_numeric": 13.2,
            },
        ],
    )

    db.refresh(order)
    db.refresh(cbc_item)
    db.refresh(eucr_item)
    db.refresh(lft_item)
    db.refresh(result)

    assert result.status == ClinicalResultStatus.FINAL
    assert cbc_item.status == ClinicalOrderStatus.COMPLETED
    assert eucr_item.status == ClinicalOrderStatus.REQUESTED
    assert lft_item.status == ClinicalOrderStatus.REQUESTED

    assert order.status == ClinicalOrderStatus.IN_PROGRESS
    assert order.completed_at is None


def test_record_final_result_completes_order(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    # The result workflow normally reaches IN_PROGRESS before reporting.
    order.status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.FINAL,
        result_data={
            "hemoglobin": 13.2,
        },
    )

    db.refresh(order)
    db.refresh(result)

    assert result.status == ClinicalResultStatus.FINAL
    assert order.status == ClinicalOrderStatus.COMPLETED
    assert order.completed_at is not None


def test_draft_laboratory_result_can_be_incomplete(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.DRAFT,
        values=[],
    )

    assert result.status == ClinicalResultStatus.DRAFT
    assert result.values == []
    assert order.status == ClinicalOrderStatus.IN_PROGRESS


def test_numeric_result_below_reference_range_is_flagged_low(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    hemoglobin = next(
        analyte
        for analyte in test.analytes
        if analyte.code == "hemoglobin"
    )

    hemoglobin.reference_low = 12
    hemoglobin.reference_high = 16
    db.commit()

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.DRAFT,
        values=[
            {
                "analyte_id": hemoglobin.id,
                "value_numeric": 10,
            },
        ],
    )

    assert result.values[0].abnormal_flag == "LOW"


def test_numeric_result_above_reference_range_is_flagged_high(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    hemoglobin = next(
        analyte
        for analyte in test.analytes
        if analyte.code == "hemoglobin"
    )

    hemoglobin.reference_low = 12
    hemoglobin.reference_high = 16
    db.commit()

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.DRAFT,
        values=[
            {
                "analyte_id": hemoglobin.id,
                "value_numeric": 18,
            },
        ],
    )

    assert result.values[0].abnormal_flag == "HIGH"


def test_numeric_result_within_reference_range_has_no_abnormal_flag(
    db,
    hospital,
):
    context, _, _, encounter = create_test_encounter(
        db,
        hospital,
    )

    order = create_laboratory_order_by_code(
        db,
        context=context,
        encounter_id=encounter.id,
        code="CBC",
    )

    order.status = ClinicalOrderStatus.IN_PROGRESS
    db.commit()

    test = (
        db.query(LaboratoryTest)
        .filter(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code == "CBC",
        )
        .one()
    )

    hemoglobin = next(
        analyte
        for analyte in test.analytes
        if analyte.code == "hemoglobin"
    )

    hemoglobin.reference_low = 12
    hemoglobin.reference_high = 16
    db.commit()

    result = create_result_service(db).record_result(
        context=context,
        order_id=order.id,
        order_item_id=order.items[0].id,
        result_type=ClinicalResultType.LABORATORY,
        status=ClinicalResultStatus.DRAFT,
        values=[
            {
                "analyte_id": hemoglobin.id,
                "value_numeric": 14,
            },
        ],
    )

    assert result.values[0].abnormal_flag is None
