from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.modules.terminology.models.terminology_concept import (
        TerminologyConcept,
    )


class TerminologySynonym(BaseEntity):
    """
    Alternate searchable term for a terminology concept.
    """

    __tablename__ = "terminology_synonyms"

    concept_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "terminology_concepts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    term: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    concept: Mapped["TerminologyConcept"] = relationship(
        back_populates="synonyms",
    )
