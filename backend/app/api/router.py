"""
==============================================================================
LIGHTBURGH EMR

Central API Router

==============================================================================

Purpose
-------

Aggregates all feature routers into a single application router.

Each business module owns its own router.

This module composes those routers into a single API router that is
registered by `main.py`.

Architecture
------------

main.py
    │
    ▼
api_router
    ├── Identity
    ├── Organization
    ├── Staff
    ├── Patient
    ├── Episode
    ├── Encounter
    ├── Clinical Event
    ├── Laboratory
    ├── Radiology
    ├── Pharmacy
    ├── Billing
    └── ...

Adding a new module requires only:

1. Import the module router.
2. Register it with `api_router`.

No other application files should require modification.

==============================================================================
"""

from fastapi import APIRouter

# ============================================================================
# Identity
# ============================================================================

from app.modules.identity.router import (
    router as identity_router,
)

from app.modules.identity.authorization_router import (
    router as authorization_router,
)

# ============================================================================
# Organization
# ============================================================================

from app.modules.organization.router import (
    router as organization_router,
)

# ============================================================================
# Staff
# ============================================================================

from app.modules.staff.router import (
    router as staff_router,
)

# ============================================================================
# Patient
# ============================================================================

from app.modules.patients.api.patient_router import (
    router as patient_router,
)

# ============================================================================
# Episode
# ============================================================================

from app.modules.episode.api.router import (
    router as episode_router,
)

# ============================================================================
# Future Modules
# ============================================================================

# from app.modules.encounter.api.router import (
#     router as encounter_router,
# )

# from app.modules.clinical_event.api.router import (
#     router as clinical_event_router,
# )

# from app.modules.laboratory.api.router import (
#     router as laboratory_router,
# )

# from app.modules.radiology.api.router import (
#     router as radiology_router,
# )

# from app.modules.pharmacy.api.router import (
#     router as pharmacy_router,
# )

# from app.modules.billing.api.router import (
#     router as billing_router,
# )

# ============================================================================
# Central API Router
# ============================================================================

api_router = APIRouter()

# ============================================================================
# Identity
# ============================================================================

api_router.include_router(
    identity_router,
)

api_router.include_router(
    authorization_router,
)

# ============================================================================
# Organization
# ============================================================================

api_router.include_router(
    organization_router,
)

# ============================================================================
# Staff
# ============================================================================

api_router.include_router(
    staff_router,
)

# ============================================================================
# Patient
# ============================================================================

api_router.include_router(
    patient_router,
)

# ============================================================================
# Episode
# ============================================================================

api_router.include_router(
    episode_router,
)

# ============================================================================
# Future Modules
# ============================================================================

# api_router.include_router(
#     encounter_router,
# )

# api_router.include_router(
#     clinical_event_router,
# )

# api_router.include_router(
#     laboratory_router,
# )

# api_router.include_router(
#     radiology_router,
# )

# api_router.include_router(
#     pharmacy_router,
# )

# api_router.include_router(
#     billing_router,
# )