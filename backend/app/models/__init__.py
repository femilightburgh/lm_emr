"""
==============================================================================
LIGHTBURGH EMR
SQLAlchemy Model Registry
==============================================================================

Purpose
-------
This module serves as the central SQLAlchemy model registry for the
application.

Alembic and SQLAlchemy must import every ORM model before mapper
configuration. Importing the models here ensures:

    • All ORM mappers are registered.
    • Relationship references using string class names are resolved.
    • Base.metadata contains every table definition.
    • Alembic autogeneration detects schema changes correctly.

Failure to register models here may result in:

    • InvalidRequestError:
      "expression 'ModelName' failed to locate a name"

    • Empty Alembic migrations

    • Missing tables during migration generation

Guidelines
----------
Whenever a new ORM model is created, it must be imported here.

Example:

    from app.modules.billing.models import Invoice

and added to __all__.

==============================================================================
"""

# ============================================================================
# Organization
# ============================================================================

from app.modules.organization.models import (
    Department,
    Hospital,
)


# ============================================================================
# Identity
# ============================================================================

from app.modules.identity.models import (
    Permission,
    Role,
    RolePermission,
    UserAccount,
    UserRole,
)

from app.modules.identity.invitation_models import (
    UserInvitation,
)


# ============================================================================
# Patients
# ============================================================================

from app.modules.patients.models import Patient


# ============================================================================
# Staff
# ============================================================================

from app.modules.staff.models import (
    Staff,
    StaffEmployment,
)


# ============================================================================
# Encounter
# ============================================================================
from app.modules.encounter.models import Encounter, EncounterStatus
from app.modules.events.models import ClinicalEvent
from app.modules.clinical_documents.models import ClinicalDocument
from app.modules.clinical_orders.models import ClinicalOrder
from app.modules.pharmacy.models import Dispensing
from app.modules.laboratory.models import (
    LaboratoryTest,
    LaboratoryTestAnalyte,
)

from app.modules.clinical_orders.models import (
    MedicationTreatment,
    MedicationTreatmentStatus,
    MedicationDose,
    MedicationDoseStatus,
    MedicationAdministration,
    MedicationAdministrationStatus,
)
from app.modules.clinical_results.models import (
    ClinicalResult,
    ClinicalResultValue,
)
from app.modules.diagnostics.models import (
    DiagnosticInvestigation,
    DiagnosticReport,
    DiagnosticReportAttachment,
)
from app.modules.diagnoses.models import ClinicalDiagnosis
from app.modules.terminology.models import (
    TerminologyConcept,
    TerminologySynonym,
)

# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    # Organization
    "Hospital",
    "Department",

    # Identity
    "UserAccount",
    "UserInvitation",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",

    # Patients
    "Patient",

    # Staff
    "Staff",
    "StaffEmployment",

    # Encounter
    "Encounter",
    "EncounterStatus",

    # Events
    "ClinicalEvent",

    # Clinical Documents
    "ClinicalDocument",

    # Clinical Orders
    "ClinicalOrder",
    "Dispensing",

    # Laboratory
    "LaboratoryTest",
    "LaboratoryTestAnalyte",

    # Inpatient Medication
    "MedicationTreatment",
    "MedicationTreatmentStatus",
    "MedicationDose",
    "MedicationDoseStatus",
    "MedicationAdministration",
    "MedicationAdministrationStatus",

    # Clinical Results
    "ClinicalResult",
    "ClinicalResultValue",

    # Diagnostics
    "DiagnosticInvestigation",
    "DiagnosticReport",
    "DiagnosticReportAttachment",

    # Clinical Diagnoses
    "ClinicalDiagnosis",

    # Terminology
    "TerminologyConcept",
    "TerminologySynonym",
]