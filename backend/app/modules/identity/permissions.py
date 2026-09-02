"""
========================================================================

LIGHTBURGH EMR

System Permissions

========================================================================

Purpose
-------

Defines the canonical permission codes supported by LIGHTBURGH.

Permissions are platform capabilities.

Hospitals assign these permissions to their own custom roles.

Do NOT hard-code role names throughout the application.

========================================================================
"""


class Permissions:
    """
    Canonical permission codes.

    Permission naming convention:

        <resource>.<action>
    """

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------

    PATIENT_READ = "patient.read"
    PATIENT_CREATE = "patient.create"
    PATIENT_UPDATE = "patient.update"
    PATIENT_DELETE = "patient.delete"

    # ------------------------------------------------------------------
    # Staff
    # ------------------------------------------------------------------

    STAFF_READ = "staff.read"
    STAFF_CREATE = "staff.create"
    STAFF_UPDATE = "staff.update"
    STAFF_DELETE = "staff.delete"

    # ------------------------------------------------------------------
    # Departments
    # ------------------------------------------------------------------

    DEPARTMENT_READ = "department.read"
    DEPARTMENT_CREATE = "department.create"
    DEPARTMENT_UPDATE = "department.update"
    DEPARTMENT_DELETE = "department.delete"

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    ROLE_READ = "role.read"
    ROLE_CREATE = "role.create"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"

    PERMISSION_ASSIGN = "permission.assign"

    # ------------------------------------------------------------------
    # Vitals
    # ------------------------------------------------------------------

    VITALS_CREATE = "vitals.create"

    # ------------------------------------------------------------------
    # Clinical Orders
    # ------------------------------------------------------------------

    CLINICAL_ORDER_CREATE = "clinical_order.create"
    CLINICAL_ORDER_READ = "clinical_order.read"
    CLINICAL_ORDER_CANCEL = "clinical_order.cancel"

    MEDICATION_ADMINISTRATION_READ = (
        "medication_administration.read"
    )
    MEDICATION_ADMINISTRATION_CREATE = (
        "medication_administration.create"
    )

    LABORATORY_CATALOGUE_READ = "laboratory_catalogue.read"
    LABORATORY_CATALOGUE_UPDATE = "laboratory_catalogue.update"

    DIAGNOSIS_CREATE = "diagnosis.create"
    DIAGNOSIS_READ = "diagnosis.read"

    TERMINOLOGY_READ = "terminology.read"

    # ------------------------------------------------------------------
    # Clinical Results
    # ------------------------------------------------------------------

    CLINICAL_RESULT_CREATE = "clinical_result.create"
    CLINICAL_RESULT_READ = "clinical_result.read"

    # ------------------------------------------------------------------
    # Hospital
    # ------------------------------------------------------------------

    HOSPITAL_SETTINGS_UPDATE = (
        "hospital.settings.update"
    )