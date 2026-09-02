"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Report Model
==============================================================================
"""

from typing import Any
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Enum as SqlEnum,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.clinical_results.enums import ClinicalResultStatus
from app.modules.diagnostics.enums import DiagnosticCategory


class DiagnosticReport(BaseEntity):
    """
    Report recorded against a diagnostic clinical order.
    """

    __tablename__ = "diagnostic_reports"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinical_orders.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    investigation_id: Mapped[UUID] = mapped_column(
        ForeignKey("diagnostic_investigations.id"),
        nullable=False,
        index=True,
    )

    category: Mapped[DiagnosticCategory] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[ClinicalResultStatus] = mapped_column(
        SqlEnum(
            ClinicalResultStatus,
            name="diagnostic_report_status_enum",
        ),
        nullable=False,
        default=ClinicalResultStatus.DRAFT,
    )

    findings: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    impression: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    interpretation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommendations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    recorded_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
        index=True,
    )

    recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    measurements: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    investigation = relationship(
        "DiagnosticInvestigation",
        back_populates="reports",
    )

    recording_staff = relationship(
        "Staff",
        foreign_keys=[recorded_by],
    )

    attachments = relationship(
        "DiagnosticReportAttachment",
        back_populates="report",
        cascade="all, delete-orphan",
    )
