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
# Public Exports
# ============================================================================

__all__ = [
    # Organization
    "Hospital",
    "Department",

    # Identity
    "UserAccount",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",

    # Patients
    "Patient",

    # Staff
    "Staff",
    "StaffEmployment",
]