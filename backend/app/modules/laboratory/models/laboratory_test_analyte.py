from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum as SqlEnum,
    ForeignKey,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.laboratory.enums import LaboratoryAnalyteDataType


class LaboratoryTestAnalyte(BaseEntity):
    """
    A structured analyte/field belonging to a laboratory test definition.
    """

    __tablename__ = "laboratory_test_analytes"

    __table_args__ = (
        UniqueConstraint(
            "laboratory_test_id",
            "code",
            name="uq_laboratory_test_analyte_code",
        ),
    )

    laboratory_test_id: Mapped[UUID] = mapped_column(
        ForeignKey("laboratory_tests.id"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    data_type: Mapped[LaboratoryAnalyteDataType] = mapped_column(
        SqlEnum(
            LaboratoryAnalyteDataType,
            name="laboratory_analyte_data_type_enum",
        ),
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reference_low: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    reference_high: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    reference_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    options: Mapped[list[Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    display_order: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    laboratory_test = relationship(
        "LaboratoryTest",
        back_populates="analytes",
    )
