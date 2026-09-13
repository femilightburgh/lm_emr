"""
==============================================================================
LIGHTBURGH EMR

Grouped Investigation Order Tests
==============================================================================
"""

from sqlalchemy import select

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import ClinicalOrderType
from app.modules.clinical_orders.models import (
    ClinicalOrder,
    ClinicalOrderItem,
    ClinicalOrderItemType,
)
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
    MedicationTreatmentRepository,
    PrescriptionRepository,
)
from app.modules.clinical_orders.services import (
    ClinicalOrderService,
    InpatientMedicationService,
)
from app.modules.diagnostics.repositories.diagnostic_repository import (
    DiagnosticRepository,
)
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.events.repositories import ClinicalEventRepository
from app.modules.events.services import ClinicalEventService
from app.modules.laboratory.models import LaboratoryTest
from app.modules.laboratory.repositories.laboratory_test_repository import (
    LaboratoryTestRepository,
)
from app.modules.staff.repository import StaffRepository


def build_service(db) -> ClinicalOrderService:
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
        inpatient_medication_service=InpatientMedicationService(
            db=db,
            episode_repository=EpisodeRepository(db),
            treatment_repository=MedicationTreatmentRepository(db),
        ),
    )


def test_laboratory_order_groups_multiple_tests_into_one_order(
    db,
):
    from tests.laboratory.test_laboratory_router import (
        create_hospital,
        create_user,
    )
    from tests.clinical_orders.test_router import (
        create_doctor_encounter,
    )

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    tests = db.scalars(
        select(LaboratoryTest)
        .where(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code.in_(["APTT", "BCS", "CBC"]),
            LaboratoryTest.active.is_(True),
        )
        .order_by(LaboratoryTest.code)
    ).all()

    assert [test.code for test in tests] == [
        "APTT",
        "BCS",
        "CBC",
    ]

    context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = build_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
        items=[
            {"laboratory_test_id": test.id}
            for test in tests
        ],
    )

    db.refresh(order)

    saved_items = db.scalars(
        select(ClinicalOrderItem)
        .where(
            ClinicalOrderItem.clinical_order_id == order.id,
        )
        .order_by(ClinicalOrderItem.display_order)
    ).all()

    assert order.order_type == ClinicalOrderType.LABORATORY
    assert len(saved_items) == 3

    assert {
        item.item_type
        for item in saved_items
    } == {
        ClinicalOrderItemType.LABORATORY,
    }

    assert [
        item.details["test_code"]
        for item in saved_items
    ] == [
        "APTT",
        "BCS",
        "CBC",
    ]

    assert {
        item.laboratory_test_id
        for item in saved_items
    } == {
        test.id
        for test in tests
    }

    parent_orders = db.scalars(
        select(ClinicalOrder)
        .where(
            ClinicalOrder.encounter_id == encounter.id,
            ClinicalOrder.order_type == ClinicalOrderType.LABORATORY,
        )
    ).all()

    assert len(parent_orders) == 1
    assert parent_orders[0].id == order.id


def test_grouped_laboratory_items_can_be_received_independently(
    db,
):
    from tests.laboratory.test_laboratory_router import (
        create_hospital,
        create_user,
    )
    from tests.clinical_orders.test_router import (
        create_doctor_encounter,
    )

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    laboratory_tests = db.scalars(
        select(LaboratoryTest)
        .where(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code.in_(["APTT", "BCS", "CBC"]),
            LaboratoryTest.active.is_(True),
        )
        .order_by(LaboratoryTest.code)
    ).all()

    context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = build_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
        items=[
            {"laboratory_test_id": test.id}
            for test in laboratory_tests
        ],
    )

    target_item = next(
        item
        for item in order.items
        if item.details["test_code"] == "CBC"
    )

    sibling_items = [
        item
        for item in order.items
        if item.id != target_item.id
    ]

    updated_order = service.receive_order_item(
        context=context,
        order_item_id=target_item.id,
    )

    updated_target = next(
        item
        for item in updated_order.items
        if item.id == target_item.id
    )

    assert updated_target.status.value == "RECEIVED"

    for sibling in sibling_items:
        updated_sibling = next(
            item
            for item in updated_order.items
            if item.id == sibling.id
        )
        assert updated_sibling.status.value == "REQUESTED"

    assert updated_order.status.value == "REQUESTED"


def test_grouped_laboratory_items_can_start_independently(
    db,
):
    from tests.laboratory.test_laboratory_router import (
        create_hospital,
        create_user,
    )
    from tests.clinical_orders.test_router import (
        create_doctor_encounter,
    )

    hospital = create_hospital(db)

    doctor_user = create_user(
        db,
        hospital=hospital,
        role_name="Doctor",
    )

    _, encounter = create_doctor_encounter(
        db,
        hospital,
        doctor_user,
    )

    laboratory_tests = db.scalars(
        select(LaboratoryTest)
        .where(
            LaboratoryTest.hospital_id == hospital.id,
            LaboratoryTest.code.in_(["APTT", "BCS", "CBC"]),
            LaboratoryTest.active.is_(True),
        )
        .order_by(LaboratoryTest.code)
    ).all()

    context = RequestContext(
        user_id=doctor_user.id,
        hospital_id=hospital.id,
        permissions=frozenset(),
    )

    service = build_service(db)

    order = service.create_order(
        context=context,
        encounter_id=encounter.id,
        order_type=ClinicalOrderType.LABORATORY,
        priority="ROUTINE",
        details={
            "test_code": "CBC",
            "test_name": "Full Blood Count",
        },
        items=[
            {"laboratory_test_id": test.id}
            for test in laboratory_tests
        ],
    )

    target_item = next(
        item
        for item in order.items
        if item.details["test_code"] == "CBC"
    )

    service.receive_order_item(
        context=context,
        order_item_id=target_item.id,
    )

    updated_order = service.start_order_item(
        context=context,
        order_item_id=target_item.id,
    )

    updated_target = next(
        item
        for item in updated_order.items
        if item.id == target_item.id
    )

    assert updated_target.status.value == "IN_PROGRESS"

    sibling_statuses = {
        item.details["test_code"]: item.status.value
        for item in updated_order.items
        if item.id != target_item.id
    }

    assert sibling_statuses == {
        "APTT": "REQUESTED",
        "BCS": "REQUESTED",
    }

    assert updated_order.status.value == "REQUESTED"
