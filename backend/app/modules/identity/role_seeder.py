"""
========================================================================

LIGHTBURGH EMR

Role Seeder

========================================================================

Purpose
-------

Seeds the default system roles for a newly created hospital.

This module is idempotent.

Running it multiple times will never create duplicate roles.

========================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import Role


DEFAULT_ROLES = [
    (
        "Administrator",
        "Full administrative access to the hospital.",
    ),
    (
        "Doctor",
        "Medical practitioner responsible for patient care.",
    ),
    (
        "Nurse",
        "Nursing staff responsible for patient care.",
    ),
    (
        "Receptionist",
        "Registers patients and manages appointments.",
    ),
    (
        "Medical Records Officer",
        "Maintains patient records.",
    ),
    (
        "Laboratory Scientist",
        "Performs laboratory investigations.",
    ),
    (
        "Radiographer",
        "Performs radiology investigations.",
    ),
    (
        "Pharmacist",
        "Dispenses medications.",
    ),
    (
        "Cashier",
        "Processes patient payments.",
    ),
    (
        "Accountant",
        "Manages financial records.",
    ),
    (
        "IT Administrator",
        "Maintains hospital IT infrastructure.",
    ),
]


def seed_default_roles(
    db: Session,
    hospital_id: UUID,
) -> None:
    """
    Seed default roles for a hospital.

    Safe to execute multiple times.
    """

    for role_name, description in DEFAULT_ROLES:

        existing = db.scalar(
            select(Role).where(
                Role.hospital_id == hospital_id,
                Role.name == role_name,
            )
        )

        if existing:
            continue

        db.add(
            Role(
                hospital_id=hospital_id,
                name=role_name,
                description=description,
                is_system_role=True,
            )
        )