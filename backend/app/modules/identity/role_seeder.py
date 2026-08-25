"""
========================================================================

LIGHTBURGH EMR

Role Seeder

========================================================================

Purpose
-------

Seeds the default system roles for a newly created hospital and assigns
the appropriate platform permissions to those roles.

This module is idempotent.

Running it multiple times will never create duplicate roles or duplicate
role-permission assignments.

========================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import Role
from app.modules.identity.permissions import Permissions
from app.modules.identity.permission_repository import (
    PermissionRepository,
)
from app.modules.identity.role_permission_repository import (
    RolePermissionRepository,
)
from app.modules.identity.role_permission_service import (
    RolePermissionService,
)


DEFAULT_ROLES = [
    (
        "Administrator",
        "Full administrative access to the hospital.",
        [
            Permissions.PATIENT_READ,
            Permissions.PATIENT_CREATE,
            Permissions.PATIENT_UPDATE,
        ],
    ),
    (
        "Doctor",
        "Medical practitioner responsible for patient care.",
        [
            Permissions.PATIENT_READ,
            Permissions.PATIENT_UPDATE,
            Permissions.CLINICAL_ORDER_CREATE,
            Permissions.CLINICAL_ORDER_READ,
            Permissions.CLINICAL_ORDER_CANCEL,
            Permissions.CLINICAL_RESULT_READ,
            Permissions.DIAGNOSIS_CREATE,
            Permissions.DIAGNOSIS_READ,
            Permissions.TERMINOLOGY_READ,
        ],
    ),
    (
        "Nurse",
        "Nursing staff responsible for patient care.",
        [
            Permissions.PATIENT_READ,
            Permissions.PATIENT_UPDATE,
            Permissions.CLINICAL_ORDER_READ,
            Permissions.CLINICAL_RESULT_READ,
            Permissions.DIAGNOSIS_READ,
            Permissions.TERMINOLOGY_READ,
        ],
    ),
    (
        "Receptionist",
        "Registers patients and manages appointments.",
        [
            Permissions.PATIENT_READ,
            Permissions.PATIENT_CREATE,
            Permissions.PATIENT_UPDATE,
        ],
    ),
    (
        "Medical Records Officer",
        "Maintains patient records.",
        [
            Permissions.PATIENT_READ,
            Permissions.PATIENT_CREATE,
            Permissions.PATIENT_UPDATE,
            Permissions.DIAGNOSIS_READ,
            Permissions.TERMINOLOGY_READ,
        ],
    ),
    (
        "Laboratory Scientist",
        "Performs laboratory investigations.",
        [
            Permissions.PATIENT_READ,
            Permissions.CLINICAL_ORDER_READ,
            Permissions.CLINICAL_RESULT_CREATE,
        ],
    ),
    (
        "Radiographer",
        "Performs radiology investigations.",
        [
            Permissions.PATIENT_READ,
            Permissions.CLINICAL_ORDER_READ,
            Permissions.CLINICAL_RESULT_CREATE,
        ],
    ),
    (
        "Pharmacist",
        "Dispenses medications.",
        [
            Permissions.PATIENT_READ,
            Permissions.CLINICAL_ORDER_READ,
        ],
    ),
    (
        "Cashier",
        "Processes patient payments.",
        [
            Permissions.PATIENT_READ,
        ],
    ),
    (
        "Accountant",
        "Manages financial records.",
        [],
    ),
    (
        "IT Administrator",
        "Maintains hospital IT infrastructure.",
        [],
    ),
]


def seed_default_roles(
    db: Session,
    hospital_id: UUID,
) -> None:
    """
    Seed default roles and their permissions for a hospital.

    Safe to execute multiple times.

    Existing roles are preserved.

    Existing permission assignments are preserved.

    Missing permission assignments are added.
    """

    role_permission_service = RolePermissionService(
        repository=RolePermissionRepository(db),
        permission_repository=PermissionRepository(db),
    )

    for (
        role_name,
        description,
        permissions,
    ) in DEFAULT_ROLES:

        role = db.scalar(
            select(Role).where(
                Role.hospital_id == hospital_id,
                Role.name == role_name,
            )
        )

        if role is None:
            role = Role(
                hospital_id=hospital_id,
                name=role_name,
                description=description,
                is_template=True,
            )

            db.add(role)
            db.flush()

        for permission_code in permissions:
            role_permission_service.assign_permission(
                role_id=role.id,
                permission_code=permission_code,
            )