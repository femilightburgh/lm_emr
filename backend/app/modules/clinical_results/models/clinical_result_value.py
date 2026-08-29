from uuid import UUID

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity


class ClinicalResultValue(BaseEntity):
    """
    A single structured value within a ClinicalResult.
    """

    __tablename__ = "clinical_result_values"

    clinical_result_id: Mapped[UUID] = mapped_column(
        ForeignKey("clinical_results.id"),
        nullable=False,
        index=True,
    )

    analyte_id: Mapped[UUID] = mapped_column(
        ForeignKey("laboratory_test_analytes.id"),
        nullable=False,
        index=True,
    )

    value_numeric: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    value_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    value_boolean: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    value_code: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    abnormal_flag: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    clinical_result = relationship(
        "ClinicalResult",
        back_populates="values",
    )

    analyte = relationship(
        "LaboratoryTestAnalyte",
    )

    @property
    def analyte_code(self) -> str:
        return self.analyte.code

    @property
    def analyte_name(self) -> str:
        return self.analyte.name

    @property
    def unit(self) -> str | None:
        return self.analyte.unit

    @property
    def reference_low(self) -> float | None:
        return (
            float(self.analyte.reference_low)
            if self.analyte.reference_low is not None
            else None
        )

    @property
    def reference_high(self) -> float | None:
        return (
            float(self.analyte.reference_high)
            if self.analyte.reference_high is not None
            else None
        )

    @property
    def reference_text(self) -> str | None:
        return self.analyte.reference_text

    @property
    def value(self):
        if self.value_numeric is not None:
            return self.value_numeric

        if self.value_text is not None:
            return self.value_text

        if self.value_boolean is not None:
            return self.value_boolean

        return self.value_code
