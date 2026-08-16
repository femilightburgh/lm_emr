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
from app.bootstrap.permissions import bootstrap_permissions


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
        bootstrap_permissions(session)
        session.commit()

        yield session

    finally:
        session.rollback()
        session.close()


def cleanup_hospital(db: Session, hospital_id) -> None:
    """
    Remove all test records belonging to a hospital.

    Cleanup follows the foreign-key dependency graph:

        encounters
          ↓
        episodes
          ↓
        patients

        staff_employments
          ↓
        staff

        departments
          ↓
        hospital
    """

    # ------------------------------------------------------------------
    # Clinical Documents
    # ------------------------------------------------------------------
    #
    # Clinical Documents belong to Encounters.
    #
    # Documents may also reference an earlier document version through
    # amended_from_id. Clear that self-reference first so the test
    # cleanup can safely remove the entire document history.
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            UPDATE clinical_documents
            SET amended_from_id = NULL
            WHERE encounter_id IN (
                SELECT e.id
                FROM encounters e
                JOIN episodes ep
                    ON e.episode_id = ep.id
                WHERE ep.hospital_id = :hospital_id
            )
            """
        ),
        {"hospital_id": hospital_id},
    )

    db.execute(
        text(
            """
            DELETE FROM clinical_documents
            WHERE encounter_id IN (
                SELECT e.id
                FROM encounters e
                JOIN episodes ep
                    ON e.episode_id = ep.id
                WHERE ep.hospital_id = :hospital_id
            )
            """
        ),
        {"hospital_id": hospital_id},
    )
    # ------------------------------------------------------------------
    # Clinical Events
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM clinical_events
            WHERE encounter_id IN (
                SELECT e.id
                FROM encounters e
                JOIN episodes ep
                    ON e.episode_id = ep.id
                WHERE ep.hospital_id = :hospital_id
            )
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Encounters
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM encounters
            WHERE episode_id IN (
                SELECT id
                FROM episodes
                WHERE hospital_id = :hospital_id
            )
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Episodes
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM episodes
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM patients
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Staff Employment History
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Staff
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM staff
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Departments
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM departments
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    db.execute(
        text(
            """
            DELETE FROM user_accounts
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    db.execute(
        text(
            """
            DELETE FROM roles
            WHERE hospital_id = :hospital_id
            """
        ),
        {"hospital_id": hospital_id},
    )

    # ------------------------------------------------------------------
    # Hospital
    # ------------------------------------------------------------------

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


def cleanup_hospital_by_code(
    db: Session,
    code: str,
) -> None:
    """
    Remove an existing test hospital identified by its code.
    """

    hospital = (
        db.query(Hospital)
        .filter(Hospital.code == code)
        .one_or_none()
    )

    if hospital is not None:
        cleanup_hospital(
            db,
            hospital.id,
        )

@pytest.fixture
def hospital(db: Session) -> Hospital:
    cleanup_hospital_by_code(
        db,
        "TEST-HOSP",
    )

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
    cleanup_hospital_by_code(
        db,
        "TEST-HOSP-2",
    )

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