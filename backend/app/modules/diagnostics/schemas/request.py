"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Request Schemas
==============================================================================
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.diagnostics.enums import DiagnosticCategory


class DiagnosticInvestigationCreateRequest(BaseModel):
    """
    Request for creating a diagnostic investigation catalogue entry.
    """

    code: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    category: DiagnosticCategory

    description: str | None = None

    report_template: dict[str, Any] = Field(
        default_factory=dict,
    )


class DiagnosticReportCreateRequest(BaseModel):
    """
    Request for creating a diagnostic report.
    """

    order_id: UUID

    investigation_id: UUID

    category: DiagnosticCategory

    findings: str | None = None

    impression: str | None = None

    interpretation: str | None = None

    recommendations: str | None = None

    measurements: dict[str, Any] | None = None


class DiagnosticReportUpdateRequest(BaseModel):
    """
    Request for updating a diagnostic report.
    """

    findings: str | None = None

    impression: str | None = None

    interpretation: str | None = None

    recommendations: str | None = None

    measurements: dict[str, Any] | None = None
