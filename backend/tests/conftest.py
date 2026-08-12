import os

import pytest
import app.models

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.modules.organization.enums import (
    HospitalOwnership,
    HospitalType,
)
from app.modules.organization.models import Hospital


TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://lm_admin:lm_password@localhost:5432/lm_emr_test",
)


engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def db() -> Session:
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def cleanup_hospital(db: Session, hospital_id) -> None:
    """
    Remove all test records belonging to a hospital.

    Cleanup order follows the foreign-key relationships:

        staff_employments
              ↓
            staff
              ↓
         departments
              ↓
           hospital
    """

    db.execute(
        text(
            """
            DELETE FROM staff_employments
            WHERE staff_id IN (
                SELECT id
                FROM staff
                WHERE hospital_id = :hospital_id
            )
            """
        ),
        {"hospital_id": hospital_id},
    )

    db.execute(
        text(
            """
            DELETE FROM staff
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    db.execute(
        text(
            """
            DELETE FROM departments
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    db.execute(
        text(
            """
            DELETE FROM hospitals
            WHERE id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    db.commit()


@pytest.fixture
def hospital(db: Session) -> Hospital:
    hospital = Hospital(
        name="Test General Hospital",
        code="TEST-HOSP",
        hospital_type=HospitalType.GENERAL,
        ownership=HospitalOwnership.PRIVATE,
        email="test@hospital.local",
        phone="08000000000",
        address="1 Test Street",
        city="Lagos",
        state="Lagos",
    )

    db.add(hospital)
    db.flush()
    db.refresh(hospital)

    yield hospital

    cleanup_hospital(db, hospital.id)


@pytest.fixture
def hospital_two(db: Session) -> Hospital:
    hospital = Hospital(
        name="Second Test Hospital",
        code="TEST-HOSP-2",
        hospital_type=HospitalType.GENERAL,
        ownership=HospitalOwnership.PRIVATE,
        email="test2@hospital.local",
        phone="08000000001",
        address="2 Test Street",
        city="Lagos",
        state="Lagos",
    )

    db.add(hospital)
    db.flush()
    db.refresh(hospital)

    yield hospital

    cleanup_hospital(db, hospital.id)