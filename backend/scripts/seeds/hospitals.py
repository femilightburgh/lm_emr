"""
========================================================

LIGHTBURGH EMR

Hospital Seeder

========================================================
"""

from sqlalchemy.orm import Session

from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.models import Hospital


def seed_hospitals(db: Session):
    """
    Seed the default LIGHTBURGH demo hospital.

    This seeder is idempotent. Running it multiple
    times will never create duplicate hospitals.
    """

    print("✓ Seeding hospitals...")

    existing = (
        db.query(Hospital)
        .filter(Hospital.code == "LIGHT001")
        .first()
    )

    if existing:
        print("  • Demo hospital already exists.")
        return

    hospital = Hospital(
        name="LIGHTBURGH Demo Hospital",
        code="LIGHT001",

        # Ownership
        ownership=HospitalOwnership.PRIVATE,

        # Facility classification
        hospital_type=HospitalType.GENERAL,

        email="info@lightburgh.com",
        phone="+2348000000000",
        website="https://lightburgh.com",
        address="No. 1 LIGHTBURGH Avenue",
        city="Ilesa",
        state="Osun",
        country="Nigeria",
        timezone="Africa/Lagos",
    )

    db.add(hospital)

    print("  • Demo hospital created.")