from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Enum as SqlEnum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.terminology.enums import TerminologySystem

if TYPE_CHECKING:
    from app.modules.terminology.models.terminology_synonym import (
        TerminologySynonym,
    )


class TerminologyConcept(BaseEntity):
    """
    Searchable clinical terminology concept.
    """

    __tablename__ = "terminology_concepts"

    __table_args__ = (
        UniqueConstraint(
            "system",
            "code",
            name="uq_terminology_concept_system_code",
        ),
    )

    system: Mapped[TerminologySystem] = mapped_column(
        SqlEnum(
            TerminologySystem,
            name="terminology_system_enum",
        ),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
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

    synonyms: Mapped[list["TerminologySynonym"]] = relationship(
        back_populates="concept",
        cascade="all, delete-orphan",
    )
