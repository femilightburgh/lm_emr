"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Report Attachment Model
==============================================================================
"""

from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity


class DiagnosticReportAttachment(BaseEntity):
    """
    File attachment associated with a diagnostic report.
    """

    __tablename__ = "diagnostic_report_attachments"

    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("diagnostic_reports.id"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    report = relationship(
        "DiagnosticReport",
        back_populates="attachments",
    )
