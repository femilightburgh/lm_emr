from app.modules.organization.department_repository import DepartmentRepository
from app.modules.organization.department_service import DepartmentService
from app.modules.organization.enums import DepartmentCategory, DepartmentStatus
from app.modules.organization.repository import HospitalRepository
 
from app.modules.organization.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
)


def test_create_department(db, hospital):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    data = DepartmentCreate(
        hospital_id=hospital.id,
        name="Emergency Department",
        code="ED",
        category=DepartmentCategory.CLINICAL,
        status=DepartmentStatus.ACTIVE,
    )

    department = service.create_department(data)

    assert department.id is not None
    assert department.hospital_id == hospital.id
    assert department.name == "Emergency Department"
    assert department.code == "ED"
    assert department.category == DepartmentCategory.CLINICAL
    assert department.status == DepartmentStatus.ACTIVE


def test_create_department_rejects_missing_hospital(db):
    from uuid import uuid4

    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    data = DepartmentCreate(
        hospital_id=uuid4(),
        name="Emergency Department",
        code="ED",
        category=DepartmentCategory.CLINICAL,
        status=DepartmentStatus.ACTIVE,
    )

    try:
        service.create_department(data)
        assert False, "Expected ValueError for missing hospital"
    except ValueError as exc:
        assert "does not exist" in str(exc)


def test_create_department_rejects_duplicate_code(db, hospital):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    first = DepartmentCreate(
        hospital_id=hospital.id,
        name="Emergency Department",
        code="ED",
        category=DepartmentCategory.CLINICAL,
        status=DepartmentStatus.ACTIVE,
    )

    service.create_department(first)

    duplicate = DepartmentCreate(
        hospital_id=hospital.id,
        name="Emergency Medicine",
        code="ED",
        category=DepartmentCategory.CLINICAL,
        status=DepartmentStatus.ACTIVE,
    )

    from app.common.exceptions import DuplicateResourceException

    try:
        service.create_department(duplicate)
        assert False, "Expected DuplicateResourceException"
    except DuplicateResourceException as exc:
        assert "already exists" in str(exc)


def test_create_department_allows_same_code_in_different_hospitals(
    db,
    hospital,
    hospital_two,
):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    first = DepartmentCreate(
        hospital_id=hospital.id,
        name="Emergency Department",
        code="ED",
        category=DepartmentCategory.CLINICAL,
        status=DepartmentStatus.ACTIVE,
    )

    second = DepartmentCreate(
        hospital_id=hospital_two.id,
        name="Emergency Department",
        code="ED",
        category=DepartmentCategory.CLINICAL,
        status=DepartmentStatus.ACTIVE,
    )

    department_one = service.create_department(first)
    department_two = service.create_department(second)

    assert department_one.code == "ED"
    assert department_two.code == "ED"
    assert department_one.hospital_id == hospital.id
    assert department_two.hospital_id == hospital_two.id
    assert department_one.id != department_two.id


def test_list_departments_returns_only_hospital_departments_in_name_order(
    db,
    hospital,
    hospital_two,
):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Radiology",
            code="RAD",
            category=DepartmentCategory.DIAGNOSTIC,
            status=DepartmentStatus.ACTIVE,
        )
    )

    service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Emergency Department",
            code="ED",
            category=DepartmentCategory.CLINICAL,
            status=DepartmentStatus.ACTIVE,
        )
    )

    service.create_department(
        DepartmentCreate(
            hospital_id=hospital_two.id,
            name="Cardiology",
            code="CARD",
            category=DepartmentCategory.CLINICAL,
            status=DepartmentStatus.ACTIVE,
        )
    )

    departments = service.list_departments(hospital.id)

    assert [department.name for department in departments] == [
        "Emergency Department",
        "Radiology",
    ]

    assert all(
        department.hospital_id == hospital.id
        for department in departments
    )

def test_update_department_supports_partial_updates(
    db,
    hospital,
):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    department = service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Emergency Department",
            code="ED",
            category=DepartmentCategory.CLINICAL,
            status=DepartmentStatus.ACTIVE,
        )
    )

    updated = service.update_department(
        department.id,
        DepartmentUpdate(
            name="Emergency Medicine",
            status=DepartmentStatus.INACTIVE,
        ),
    )

    assert updated.name == "Emergency Medicine"
    assert updated.code == "ED"
    assert updated.category == DepartmentCategory.CLINICAL
    assert updated.status == DepartmentStatus.INACTIVE
    assert updated.hospital_id == hospital.id

def test_update_department_rejects_duplicate_code(
    db,
    hospital,
):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    first = service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Emergency Department",
            code="ED",
            category=DepartmentCategory.CLINICAL,
        )
    )

    service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Radiology",
            code="RAD",
            category=DepartmentCategory.DIAGNOSTIC,
        )
    )

    from app.common.exceptions import DuplicateResourceException

    try:
        service.update_department(
            first.id,
            DepartmentUpdate(code="RAD"),
        )
        assert False, "Expected DuplicateResourceException"
    except DuplicateResourceException as exc:
        assert "already exists" in str(exc)

def test_require_active_returns_active_department(
    db,
    hospital,
):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    department = service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Emergency Department",
            code="ED",
            category=DepartmentCategory.CLINICAL,
            status=DepartmentStatus.ACTIVE,
        )
    )

    result = service.require_active(department.id)

    assert result.id == department.id
    assert result.status == DepartmentStatus.ACTIVE

def test_require_active_rejects_inactive_department(
    db,
    hospital,
):
    service = DepartmentService(
        repository=DepartmentRepository(db),
        hospital_repository=HospitalRepository(db),
    )

    department = service.create_department(
        DepartmentCreate(
            hospital_id=hospital.id,
            name="Emergency Department",
            code="ED",
            category=DepartmentCategory.CLINICAL,
            status=DepartmentStatus.INACTIVE,
        )
    )

    from app.modules.organization.exceptions import DepartmentInactiveError

    try:
        service.require_active(department.id)
        assert False, "Expected DepartmentInactiveError"
    except DepartmentInactiveError as exc:
        assert "inactive" in str(exc).lower()