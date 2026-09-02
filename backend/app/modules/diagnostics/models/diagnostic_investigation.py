"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Investigation Model
==============================================================================
"""

from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Enum as SqlEnum,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.diagnostics.enums import DiagnosticCategory


class DiagnosticInvestigation(BaseEntity):
    """
    Catalogue definition for a diagnostic investigation.
    """

    __tablename__ = "diagnostic_investigations"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "code",
            name="uq_diagnostic_investigation_hospital_code",
        ),
    )

    hospital_id: Mapped[UUID] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    category: Mapped[DiagnosticCategory] = mapped_column(
        SqlEnum(
            DiagnosticCategory,
            name="diagnostic_category_enum",
        ),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    report_template: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    reports = relationship(
        "DiagnosticReport",
        back_populates="investigation",
    )
