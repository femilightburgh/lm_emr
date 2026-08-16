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

        db.commit()

        print("\nDatabase successfully seeded.\n")

        print("Demo login")
        print("----------")
        print(f"Hospital code: {hospital.code}")
        print(f"Email:         {DEMO_USER_EMAIL}")
        print(f"Password:      {DEMO_USER_PASSWORD}")
        print(f"Role:          {DEMO_USER_ROLE}")
        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()