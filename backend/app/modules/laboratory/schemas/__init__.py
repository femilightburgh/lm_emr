"""
==============================================================================
LIGHTBURGH EMR

Laboratory Schemas
==============================================================================
"""

from app.modules.laboratory.schemas.request import (
    CreateLaboratoryAnalyteRequest,
    CreateLaboratoryTestRequest,
    UpdateLaboratoryAnalyteRequest,
    UpdateLaboratoryTestRequest,
)

from app.modules.laboratory.schemas.response import (
    LaboratoryTestAnalyteResponse,
    LaboratoryTestResponse,
)

__all__ = [
    "CreateLaboratoryAnalyteRequest",
    "CreateLaboratoryTestRequest",
    "LaboratoryTestAnalyteResponse",
    "LaboratoryTestResponse",
    "UpdateLaboratoryAnalyteRequest",
    "UpdateLaboratoryTestRequest",
]
