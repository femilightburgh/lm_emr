"""
==============================================================================
LIGHTBURGH EMR

Central API Router
==============================================================================

Purpose
-------
Aggregates all feature routers into a single application router.

Each business module owns its own router. This module simply composes
them into a single API router that is registered by `main.py`.

Architecture
------------
main.py
    │
    ▼
api_router
    ├── Identity
    ├── Organization
    ├── Staff
    ├── Patients
    ├── Appointments
    ├── Laboratory
    ├── Radiology
    ├── Pharmacy
    ├── Billing
    └── ...

Adding a new module requires only:

1. Import the module router.
2. Register it with `api_router`.

No other application files need to change.
==============================================================================
"""

from fastapi import APIRouter

# ============================================================================
# Module Routers
# ============================================================================

from app.modules.identity.router import router as identity_router
from app.modules.staff.router import router as staff_router
from app.modules.patients.api.patient_router import router as patient_router

# Future modules
# from app.modules.organization.router import router as organization_router
# from app.modules.appointments.router import router as appointment_router
# from app.modules.laboratory.router import router as laboratory_router
# from app.modules.radiology.router import router as radiology_router
# from app.modules.pharmacy.router import router as pharmacy_router
# from app.modules.billing.router import router as billing_router

# ============================================================================
# Central API Router
# ============================================================================

api_router = APIRouter()

# ============================================================================
# Registered Modules
# ============================================================================

api_router.include_router(identity_router)
api_router.include_router(staff_router)
api_router.include_router(patient_router)

# ============================================================================
# Future Modules
# ============================================================================

# api_router.include_router(organization_router)
# api_router.include_router(appointment_router)
# api_router.include_router(laboratory_router)
# api_router.include_router(radiology_router)
# api_router.include_router(pharmacy_router)
# api_router.include_router(billing_router)