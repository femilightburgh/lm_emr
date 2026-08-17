"""
========================================================================

LIGHTBURGH EMR

Core Platform Permissions

========================================================================

Purpose
-------

Defines the canonical permission catalogue for the LIGHTBURGH platform.

These permissions represent platform capabilities.

Hospitals assign these permissions to their own custom roles.

========================================================================
"""

from app.modules.identity.permission_definition import (
    PermissionDefinition,
)
from app.modules.identity.permissions import Permissions


PERMISSIONS: list[PermissionDefinition] = [

    # ==============================================================
    # Patients
    # ==============================================================

    PermissionDefinition(
        code=Permissions.PATIENT_READ,
        name="Read Patients",
        description="Allows viewing patient records within the hospital.",
    ),

    PermissionDefinition(
        code=Permissions.PATIENT_CREATE,
        name="Create Patients",
        description="Allows registering new patients.",
    ),

    PermissionDefinition(
        code=Permissions.PATIENT_UPDATE,
        name="Update Patients",
        description="Allows modifying patient information.",
    ),

    PermissionDefinition(
        code=Permissions.PATIENT_DELETE,
        name="Delete Patients",
        description="Allows deleting patient records.",
    ),

    # ==============================================================
    # Staff
    # ==============================================================

    PermissionDefinition(
        code=Permissions.STAFF_READ,
        name="Read Staff",
        description="Allows viewing staff records.",
    ),

    PermissionDefinition(
        code=Permissions.STAFF_CREATE,
        name="Create Staff",
        description="Allows creating staff records.",
    ),

    PermissionDefinition(
        code=Permissions.STAFF_UPDATE,
        name="Update Staff",
        description="Allows modifying staff records.",
    ),

    PermissionDefinition(
        code=Permissions.STAFF_DELETE,
        name="Delete Staff",
        description="Allows deleting staff records.",
    ),

    # ==============================================================
    # Departments
    # ==============================================================

    PermissionDefinition(
        code=Permissions.DEPARTMENT_READ,
        name="Read Departments",
        description="Allows viewing hospital departments.",
    ),

    PermissionDefinition(
        code=Permissions.DEPARTMENT_CREATE,
        name="Create Departments",
        description="Allows creating hospital departments.",
    ),

    PermissionDefinition(
        code=Permissions.DEPARTMENT_UPDATE,
        name="Update Departments",
        description="Allows modifying hospital departments.",
    ),

    PermissionDefinition(
        code=Permissions.DEPARTMENT_DELETE,
        name="Delete Departments",
        description="Allows deleting hospital departments.",
    ),

    # ==============================================================
    # Identity
    # ==============================================================

    PermissionDefinition(
        code=Permissions.ROLE_READ,
        name="Read Roles",
        description="Allows viewing roles.",
    ),

    PermissionDefinition(
        code=Permissions.ROLE_CREATE,
        name="Create Roles",
        description="Allows creating roles.",
    ),

    PermissionDefinition(
        code=Permissions.ROLE_UPDATE,
        name="Update Roles",
        description="Allows modifying roles.",
    ),

    PermissionDefinition(
        code=Permissions.ROLE_DELETE,
        name="Delete Roles",
        description="Allows deleting roles.",
    ),

    PermissionDefinition(
        code=Permissions.PERMISSION_ASSIGN,
        name="Assign Permissions",
        description="Allows assigning permissions to roles.",
    ),

    # ==============================================================
    # Hospital
    # ==============================================================

    PermissionDefinition(
        code=Permissions.HOSPITAL_SETTINGS_UPDATE,
        name="Update Hospital Settings",
        description="Allows modifying hospital settings.",
    ),

    # ==============================================================
    # Vitals
    # ==============================================================

    PermissionDefinition(
        code=Permissions.VITALS_CREATE,
        name="Create Vitals",
        description="Allows recording patient vital signs.",
    ),
]