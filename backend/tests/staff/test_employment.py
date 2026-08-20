from datetime import date
from uuid import UUID

from app.modules.identity.repository import IdentityRepository
from app.modules.organization.repository import HospitalRepository
from app.modules.staff.employment_repository import StaffEmploymentRepository
from app.modules.staff.enums import (
    EmploymentStatus,
    EmploymentType,
    Gender,
    Profession,
)
from app.modules.staff.exceptions import (
    CurrentEmploymentExistsError,
    DuplicateStaffNumberError,
    HospitalNotFoundError,
    InvalidEmploymentDateError,
    NoCurrentEmploymentError,
)
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import (
    StaffCreate,
    StaffEmploymentClose,
    StaffEmploymentCreate,
    StaffUpdate,
)
from app.modules.staff.service import StaffService


def test_create_staff_creates_initial_employment(db, hospital):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    data = StaffCreate(
        hospital_id=hospital.id,
        staff_number="STF-001",
        first_name="John",
        last_name="Doe",
        gender=Gender.MALE,
        date_of_birth=date(1990, 1, 15),
        profession=Profession.DOCTOR,
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
        date_employed=date(2026, 1, 1),
    )

    staff = service.create_staff(data)

    history = service.list_employment_history(staff.id)

    assert staff.id is not None
    assert staff.hospital_id == hospital.id
    assert staff.staff_number == "STF-001"

    assert len(history) == 1

    employment = history[0]

    assert employment.staff_id == staff.id
    assert employment.profession == Profession.DOCTOR
    assert employment.employment_status == EmploymentStatus.ACTIVE
    assert employment.employment_type == EmploymentType.FULL_TIME
    assert employment.date_employed == date(2026, 1, 1)
    assert employment.date_left is None


def test_get_current_employment_returns_initial_employment(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-002",
            first_name="Jane",
            last_name="Doe",
            gender=Gender.FEMALE,
            date_of_birth=date(1992, 5, 10),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 2, 1),
        )
    )

    employment = service.get_current_employment(staff.id)

    assert employment is not None
    assert employment.staff_id == staff.id
    assert employment.profession == Profession.NURSE
    assert employment.employment_status == EmploymentStatus.ACTIVE
    assert employment.employment_type == EmploymentType.FULL_TIME
    assert employment.date_employed == date(2026, 2, 1)
    assert employment.date_left is None


def test_close_current_employment(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-003",
            first_name="David",
            last_name="Smith",
            gender=Gender.MALE,
            date_of_birth=date(1988, 3, 20),
            profession=Profession.PHARMACIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2024, 1, 15),
        )
    )

    employment = service.close_current_employment(
        staff.id,
        StaffEmploymentClose(
            date_left=date(2026, 8, 1),
            employment_status=EmploymentStatus.RESIGNED,
        ),
    )

    assert employment.staff_id == staff.id
    assert employment.date_employed == date(2024, 1, 15)
    assert employment.date_left == date(2026, 8, 1)
    assert employment.employment_status == EmploymentStatus.RESIGNED


def test_closed_employment_is_retained_in_history_and_is_no_longer_current(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-004",
            first_name="Sarah",
            last_name="Johnson",
            gender=Gender.FEMALE,
            date_of_birth=date(1991, 7, 12),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2023, 6, 1),
        )
    )

    closed = service.close_current_employment(
        staff.id,
        StaffEmploymentClose(
            date_left=date(2026, 8, 1),
            employment_status=EmploymentStatus.RESIGNED,
        ),
    )

    history = service.list_employment_history(staff.id)
    current = service.get_current_employment(staff.id)

    assert len(history) == 1
    assert history[0].id == closed.id
    assert history[0].date_left == date(2026, 8, 1)
    assert history[0].employment_status == EmploymentStatus.RESIGNED

    assert current is None


def test_close_current_employment_rejects_invalid_date(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-005",
            first_name="Michael",
            last_name="Brown",
            gender=Gender.MALE,
            date_of_birth=date(1990, 4, 10),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2025, 1, 1),
        )
    )

    try:
        service.close_current_employment(
            staff.id,
            StaffEmploymentClose(
                date_left=date(2024, 12, 31),
                employment_status=EmploymentStatus.RESIGNED,
            ),
        )

        assert False, "Expected InvalidEmploymentDateError"
    except InvalidEmploymentDateError as exc:
        assert "before employment date" in str(exc)


def test_close_current_employment_rejects_when_no_current_employment(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-006",
            first_name="Robert",
            last_name="Williams",
            gender=Gender.MALE,
            date_of_birth=date(1985, 9, 5),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2020, 1, 1),
        )
    )

    service.close_current_employment(
        staff.id,
        StaffEmploymentClose(
            date_left=date(2026, 8, 1),
            employment_status=EmploymentStatus.RESIGNED,
        ),
    )

    try:
        service.close_current_employment(
            staff.id,
            StaffEmploymentClose(
                date_left=date(2026, 8, 2),
                employment_status=EmploymentStatus.TERMINATED,
            ),
        )

        assert False, "Expected NoCurrentEmploymentError"
    except NoCurrentEmploymentError as exc:
        assert "no current employment" in str(exc).lower()


def test_start_employment_creates_new_current_employment(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-007",
            first_name="Daniel",
            last_name="Okafor",
            gender=Gender.MALE,
            date_of_birth=date(1985, 6, 15),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2020, 1, 1),
        )
    )

    service.close_current_employment(
        staff.id,
        StaffEmploymentClose(
            date_left=date(2024, 12, 31),
            employment_status=EmploymentStatus.RESIGNED,
        ),
    )

    employment = service.start_employment(
        staff.id,
        StaffEmploymentCreate(
            profession=Profession.PHARMACIST,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2026, 1, 1),
        ),
    )

    assert employment.staff_id == staff.id
    assert employment.profession == Profession.PHARMACIST
    assert employment.employment_status == EmploymentStatus.ACTIVE
    assert employment.employment_type == EmploymentType.FULL_TIME
    assert employment.date_employed == date(2026, 1, 1)
    assert employment.date_left is None

    current = service.get_current_employment(staff.id)

    assert current is not None
    assert current.id == employment.id

    history = service.list_employment_history(staff.id)

    assert len(history) == 2
    assert history[0].id == employment.id
    assert history[1].date_left == date(2024, 12, 31)


def test_start_employment_rejects_when_current_employment_exists(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-008",
            first_name="Grace",
            last_name="Adeyemi",
            gender=Gender.FEMALE,
            date_of_birth=date(1990, 2, 10),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2025, 1, 1),
        )
    )

    try:
        service.start_employment(
            staff.id,
            StaffEmploymentCreate(
                profession=Profession.DOCTOR,
                employment_status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                date_employed=date(2026, 1, 1),
            ),
        )

        assert False, "Expected CurrentEmploymentExistsError"

    except CurrentEmploymentExistsError as exc:
        assert "already has current employment" in str(exc).lower()


def test_start_employment_rejects_date_before_date_of_birth(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-009",
            first_name="Peter",
            last_name="James",
            gender=Gender.MALE,
            date_of_birth=date(1990, 5, 10),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2020, 1, 1),
        )
    )

    service.close_current_employment(
        staff.id,
        StaffEmploymentClose(
            date_left=date(2024, 12, 31),
            employment_status=EmploymentStatus.RESIGNED,
        ),
    )

    try:
        service.start_employment(
            staff.id,
            StaffEmploymentCreate(
                profession=Profession.DOCTOR,
                employment_status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                date_employed=date(1989, 1, 1),
            ),
        )

        assert False, "Expected InvalidEmploymentDateError"

    except InvalidEmploymentDateError as exc:
        assert "before date of birth" in str(exc).lower()


def test_update_staff_updates_staff_information_without_changing_employment(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-010",
            first_name="Andrew",
            last_name="Brown",
            gender=Gender.MALE,
            date_of_birth=date(1990, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2025, 1, 1),
        )
    )

    original_employment = service.get_current_employment(staff.id)

    updated = service.update_staff(
        staff.id,
        StaffUpdate(
            first_name="Andrew",
            last_name="Williams",
            phone_number="08012345678",
        ),
    )

    assert updated.id == staff.id
    assert updated.first_name == "Andrew"
    assert updated.last_name == "Williams"
    assert updated.phone_number == "08012345678"

    current = service.get_current_employment(staff.id)

    assert current is not None
    assert current.id == original_employment.id
    assert current.profession == Profession.DOCTOR
    assert current.employment_status == EmploymentStatus.ACTIVE


def test_create_staff_rejects_duplicate_staff_number(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-011",
            first_name="John",
            last_name="Doe",
            gender=Gender.MALE,
            date_of_birth=date(1990, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2025, 1, 1),
        )
    )

    try:
        service.create_staff(
            StaffCreate(
                hospital_id=hospital.id,
                staff_number="STF-011",
                first_name="Jane",
                last_name="Doe",
                gender=Gender.FEMALE,
                date_of_birth=date(1992, 1, 1),
                profession=Profession.NURSE,
                employment_status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                date_employed=date(2025, 2, 1),
            )
        )

        assert False, "Expected DuplicateStaffNumberError"

    except DuplicateStaffNumberError as exc:
        assert "already exists" in str(exc).lower()


def test_create_staff_allows_same_staff_number_in_different_hospital(
    db,
    hospital,
    hospital_two,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    first_staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital.id,
            staff_number="STF-012",
            first_name="John",
            last_name="Doe",
            gender=Gender.MALE,
            date_of_birth=date(1990, 1, 1),
            profession=Profession.DOCTOR,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2025, 1, 1),
        )
    )

    second_staff = service.create_staff(
        StaffCreate(
            hospital_id=hospital_two.id,
            staff_number="STF-012",
            first_name="Jane",
            last_name="Doe",
            gender=Gender.FEMALE,
            date_of_birth=date(1992, 1, 1),
            profession=Profession.NURSE,
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            date_employed=date(2025, 2, 1),
        )
    )

    assert first_staff.id != second_staff.id
    assert first_staff.hospital_id == hospital.id
    assert second_staff.hospital_id == hospital_two.id
    assert first_staff.staff_number == "STF-012"
    assert second_staff.staff_number == "STF-012"


def test_create_staff_rejects_nonexistent_hospital(db):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    try:
        service.create_staff(
            StaffCreate(
                hospital_id=UUID(
                    "00000000-0000-0000-0000-000000000001"
                ),
                staff_number="STF-013",
                first_name="John",
                last_name="Doe",
                gender=Gender.MALE,
                date_of_birth=date(1990, 1, 1),
                profession=Profession.DOCTOR,
                employment_status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                date_employed=date(2025, 1, 1),
            )
        )

        assert False, "Expected HospitalNotFoundError"

    except HospitalNotFoundError as exc:
        assert "does not exist" in str(exc).lower()


def test_create_staff_rejects_employment_date_before_date_of_birth(
    db,
    hospital,
):
    service = StaffService(
        repository=StaffRepository(db),
        hospital_repository=HospitalRepository(db),
        employment_repository=StaffEmploymentRepository(db),
        identity_repository=IdentityRepository(db),
    )

    try:
        service.create_staff(
            StaffCreate(
                hospital_id=hospital.id,
                staff_number="STF-014",
                first_name="James",
                last_name="Brown",
                gender=Gender.MALE,
                date_of_birth=date(1990, 5, 10),
                profession=Profession.DOCTOR,
                employment_status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                date_employed=date(1989, 1, 1),
            )
        )

        assert False, "Expected InvalidEmploymentDateError"

    except InvalidEmploymentDateError as exc:
        assert "before date of birth" in str(exc).lower()