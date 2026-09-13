"""
==============================================================================
LIGHTBURGH EMR

Laboratory Test Model
==============================================================================
"""

from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity


class LaboratoryTest(BaseEntity):
    """
    Catalogue definition for a laboratory investigation.
    """

    __tablename__ = "laboratory_tests"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "code",
            name="uq_laboratory_test_hospital_code",
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

    specimen: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    hospital = relationship(
        "Hospital",
        back_populates="laboratory_tests",
    )

    analytes = relationship(
        "LaboratoryTestAnalyte",
        back_populates="laboratory_test",
        cascade="all, delete-orphan",
        order_by="LaboratoryTestAnalyte.display_order",
    )
