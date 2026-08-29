"""
========================================================

LIGHTBURGH EMR

Database Seeder

========================================================

Usage

python -m scripts.seed

========================================================
"""

import app.models

from app.bootstrap.permissions import bootstrap_permissions
from app.db.session import SessionLocal
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.user_service import UserService
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
from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.schemas import HospitalCreate
from app.modules.organization.service import HospitalService


DEMO_HOSPITAL = HospitalCreate(
    name="LIGHTBURGH Demo Hospital",
    code="LIGHT001",
    hospital_type=HospitalType.GENERAL,
    ownership=HospitalOwnership.PRIVATE,
    email="info@lightburgh.com",
    phone="+2348000000000",
    website="https://lightburgh.com",
    address="No. 1 LIGHTBURGH Avenue",
    city="Ilesa",
    state="Osun",
    country="Nigeria",
    timezone="Africa/Lagos",
)


DEMO_USER_EMAIL = "receptionist@lightburgh.com"
DEMO_USER_PASSWORD = "password123"
DEMO_USER_ROLE = "Receptionist"

DEMO_DOCTOR_EMAIL = "doctor@lightburgh.com"
DEMO_DOCTOR_PASSWORD = "password123"
DEMO_DOCTOR_ROLE = "Doctor"
DEMO_DOCTOR_STAFF_NUMBER = "STF-DEMO-DOCTOR"


def seed_database() -> None:
    print("\n==============================")
    print("LIGHTBURGH Database Seeding")
    print("==============================\n")

    db = SessionLocal()

    try:
        # --------------------------------------------------------------
        # Platform permissions
        # --------------------------------------------------------------

        print("✓ Seeding permissions...")

        bootstrap_permissions(db)

        # --------------------------------------------------------------
        # Hospital
        # --------------------------------------------------------------

        print("✓ Seeding hospital...")

        hospital_service = HospitalService(db)

        hospital = hospital_service.repository.get_hospital_by_code(
            DEMO_HOSPITAL.code,
        )

        if hospital is None:
            hospital = hospital_service.create_hospital(
                DEMO_HOSPITAL,
            )

            print(
                f"  • Created hospital: "
                f"{DEMO_HOSPITAL.code}"
            )
        else:
            print(
                f"  • Hospital already exists: "
                f"{DEMO_HOSPITAL.code}"
            )

        # --------------------------------------------------------------
        # Demo receptionist
        # --------------------------------------------------------------

        print("✓ Seeding users...")

        repository = IdentityRepository(db)

        existing_user = repository.get_user_by_email(
            hospital_id=hospital.id,
            email=DEMO_USER_EMAIL,
        )

        if existing_user is None:
            user_service = UserService(repository)

            user_service.create_user(
                hospital_code=hospital.code,
                email=DEMO_USER_EMAIL,
                password=DEMO_USER_PASSWORD,
                role_name=DEMO_USER_ROLE,
            )

            print(
                f"  • Created {DEMO_USER_ROLE}: "
                f"{DEMO_USER_EMAIL}"
            )
        else:
            print(
                f"  • User already exists: "
                f"{DEMO_USER_EMAIL}"
            )

        # --------------------------------------------------------------
        # Demo Doctor
        # --------------------------------------------------------------

        doctor_repository = IdentityRepository(db)

        doctor_user = doctor_repository.get_user_by_email(
            hospital_id=hospital.id,
            email=DEMO_DOCTOR_EMAIL,
        )

        if doctor_user is None:
            doctor_service = UserService(
                doctor_repository,
            )

            doctor_user = doctor_service.create_user(
                hospital_code=hospital.code,
                email=DEMO_DOCTOR_EMAIL,
                password=DEMO_DOCTOR_PASSWORD,
                role_name=DEMO_DOCTOR_ROLE,
            )

            print(
                f"  • Created {DEMO_DOCTOR_ROLE}: "
                f"{DEMO_DOCTOR_EMAIL}"
            )
        else:
            print(
                f"  • User already exists: "
                f"{DEMO_DOCTOR_EMAIL}"
            )

        staff_repository = StaffRepository(db)

        doctor_staff = (
            staff_repository.get_by_staff_number(
                hospital_id=hospital.id,
                staff_number=DEMO_DOCTOR_STAFF_NUMBER,
            )
        )

        if doctor_staff is None:
            staff_service = StaffService(
                repository=staff_repository,
                hospital_repository=hospital_service.repository,
                employment_repository=(
                    StaffEmploymentRepository(db)
                ),
                identity_repository=doctor_repository,
            )

            doctor_staff = staff_service.create_staff(
                StaffCreate(
                    hospital_id=hospital.id,
                    staff_number=DEMO_DOCTOR_STAFF_NUMBER,
                    first_name="Demo",
                    last_name="Doctor",
                    gender=Gender.MALE,
                    date_of_birth=__import__("datetime").date(
                        1985,
                        1,
                        1,
                    ),
                    profession=Profession.DOCTOR,
                    employment_status=EmploymentStatus.ACTIVE,
                    employment_type=EmploymentType.FULL_TIME,
                    date_employed=__import__("datetime").date(
                        2026,
                        1,
                        1,
                    ),
                )
            )

            staff_service.link_user_account(
                doctor_staff.id,
                doctor_user.id,
            )

            print(
                f"  • Created Doctor Staff profile and linked account: "
                f"{DEMO_DOCTOR_STAFF_NUMBER}"
            )
        elif doctor_staff.user_account_id != doctor_user.id:
            staff_service = StaffService(
                repository=staff_repository,
                hospital_repository=hospital_service.repository,
                employment_repository=(
                    StaffEmploymentRepository(db)
                ),
                identity_repository=doctor_repository,
            )

            staff_service.link_user_account(
                doctor_staff.id,
                doctor_user.id,
            )

            print(
                f"  • Linked Doctor Staff profile: "
                f"{DEMO_DOCTOR_STAFF_NUMBER}"
            )
        else:
            print(
                f"  • Doctor Staff profile already exists: "
                f"{DEMO_DOCTOR_STAFF_NUMBER}"
            )

        db.commit()

        print("\nDatabase successfully seeded.\n")

        print("Demo login")
        print("----------")
        print(f"Hospital code: {hospital.code}")
        print(f"Email:         {DEMO_USER_EMAIL}")
        print(f"Password:      {DEMO_USER_PASSWORD}")
        print(f"Role:          {DEMO_USER_ROLE}")
        print()
        print("Demo doctor login")
        print("------------------")
        print(f"Hospital code: {hospital.code}")
        print(f"Email:         {DEMO_DOCTOR_EMAIL}")
        print(f"Password:      {DEMO_DOCTOR_PASSWORD}")
        print(f"Role:          {DEMO_DOCTOR_ROLE}")
        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()