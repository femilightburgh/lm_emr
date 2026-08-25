from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.models import (
    TerminologyConcept,
    TerminologySynonym,
)


class TerminologyRepository:
    """
    Persistence operations for terminology concepts.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_concept(
        self,
        *,
        concept: TerminologyConcept,
    ) -> TerminologyConcept:
        self.db.add(concept)
        return concept

    def create_synonym(
        self,
        *,
        synonym: TerminologySynonym,
    ) -> TerminologySynonym:
        self.db.add(synonym)
        return synonym

    def get_by_system_and_code(
        self,
        *,
        system: TerminologySystem,
        code: str,
    ) -> TerminologyConcept | None:
        statement = (
            select(TerminologyConcept)
            .where(
                TerminologyConcept.system == system,
                TerminologyConcept.code == code,
            )
        )

        return self.db.scalar(statement)

    def search(
        self,
        *,
        query: str,
        system: TerminologySystem | None = None,
        limit: int = 20,
    ) -> list[TerminologyConcept]:
        """
        Search active terminology concepts by code, display name,
        or synonym.

        Matching is case-insensitive.
        """

        normalized = query.strip()

        if not normalized:
            return []

        pattern = f"%{normalized}%"

        statement = (
            select(TerminologyConcept)
            .outerjoin(
                TerminologySynonym,
                TerminologySynonym.concept_id == TerminologyConcept.id,
            )
            .where(
                TerminologyConcept.active.is_(True),
                or_(
                    TerminologyConcept.code.ilike(pattern),
                    TerminologyConcept.display_name.ilike(pattern),
                    TerminologySynonym.term.ilike(pattern),
                ),
            )
            .distinct()
            .order_by(
                TerminologyConcept.display_name.asc(),
            )
            .limit(limit)
        )

        if system is not None:
            statement = statement.where(
                TerminologyConcept.system == system,
            )

        return list(
            self.db.scalars(statement),
        )

    def save(self) -> None:
        self.db.commit()

    def refresh(
        self,
        concept: TerminologyConcept,
    ) -> None:
        self.db.refresh(concept)
