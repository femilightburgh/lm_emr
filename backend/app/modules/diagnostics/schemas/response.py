"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Response Schemas
==============================================================================
"""

from typing import Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.diagnostics.enums import DiagnosticCategory


class DiagnosticInvestigationResponse(BaseModel):
    """
    Diagnostic investigation catalogue response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    code: str
    name: str
    category: DiagnosticCategory
    description: str | None
    report_template: dict[str, Any]
    active: bool


class DiagnosticReportResponse(BaseModel):
    """
    Diagnostic report response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    order_id: UUID
    investigation_id: UUID
    category: DiagnosticCategory
    status: str

    findings: str | None
    impression: str | None
    interpretation: str | None
    recommendations: str | None
    measurements: dict[str, Any] | None

    reported_at: datetime | None
    recorded_by: UUID | None
    recorded_at: datetime | None

    created_at: datetime
    updated_at: datetime


class DiagnosticReportAttachmentResponse(BaseModel):
    """
    Diagnostic report attachment response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    report_id: UUID
    file_name: str
    content_type: str
    description: str | None
    created_at: datetime
    updated_at: datetime
