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

    # ==============================================================
    # Clinical Orders
    # ==============================================================

    PermissionDefinition(
        code=Permissions.CLINICAL_ORDER_CREATE,
        name="Create Clinical Orders",
        description="Allows creating clinical orders for patient care.",
    ),

    PermissionDefinition(
        code=Permissions.CLINICAL_ORDER_READ,
        name="Read Clinical Orders",
        description="Allows viewing clinical orders for patient care.",
    ),

    PermissionDefinition(
        code=Permissions.CLINICAL_ORDER_CANCEL,
        name="Cancel Clinical Orders",
        description="Allows cancelling clinical orders that have not been completed.",
    ),

    PermissionDefinition(
        code=Permissions.LABORATORY_CATALOGUE_READ,
        name="Read Laboratory Catalogue",
        description="Allows viewing laboratory tests and analyte definitions.",
    ),

    PermissionDefinition(
        code=Permissions.LABORATORY_CATALOGUE_UPDATE,
        name="Update Laboratory Catalogue",
        description="Allows maintaining laboratory analyte metadata and reference intervals.",
    ),

    # ==============================================================
    # Clinical Diagnoses
    # ==============================================================

    PermissionDefinition(
        code=Permissions.DIAGNOSIS_CREATE,
        name="Create Clinical Diagnoses",
        description="Allows recording clinical diagnoses.",
    ),

    PermissionDefinition(
        code=Permissions.DIAGNOSIS_READ,
        name="Read Clinical Diagnoses",
        description="Allows viewing clinical diagnoses.",
    ),

    PermissionDefinition(
        code=Permissions.TERMINOLOGY_READ,
        name="Read Clinical Terminology",
        description="Allows searching supported clinical terminology.",
    ),

    # ==============================================================
    # Clinical Results
    # ==============================================================

    PermissionDefinition(
        code=Permissions.CLINICAL_RESULT_CREATE,
        name="Create Clinical Results",
        description="Allows recording results for clinical orders.",
    ),

    PermissionDefinition(
        code=Permissions.CLINICAL_RESULT_READ,
        name="Read Clinical Results",
        description="Allows viewing clinical results.",
    ),
]