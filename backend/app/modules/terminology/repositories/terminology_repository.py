from uuid import UUID

from sqlalchemy import case, exists, or_, select
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
        leaf_only: bool = True,
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

        synonym_match = exists(
            select(1)
            .select_from(TerminologySynonym)
            .where(
                TerminologySynonym.concept_id == TerminologyConcept.id,
                TerminologySynonym.term.ilike(pattern),
            )
        )

        synonym_prefix_match = exists(
            select(1)
            .select_from(TerminologySynonym)
            .where(
                TerminologySynonym.concept_id == TerminologyConcept.id,
                TerminologySynonym.term.ilike(
                    f"{normalized}%",
                ),
            )
        )

        statement = (
            select(TerminologyConcept)
            .where(
                TerminologyConcept.active.is_(True),
                or_(
                    TerminologyConcept.code.ilike(pattern),
                    TerminologyConcept.display_name.ilike(pattern),
                    synonym_match,
                ),
            )
            .order_by(
                case(
                    (
                        TerminologyConcept.code.ilike(normalized),
                        0,
                    ),
                    (
                        TerminologyConcept.display_name.ilike(normalized),
                        1,
                    ),
                    (
                        TerminologyConcept.display_name.ilike(
                            f"{normalized}%",
                        )
                        & TerminologyConcept.is_residual.is_(False),
                        2,
                    ),
                    (
                        TerminologyConcept.display_name.ilike(
                            f"{normalized}%",
                        ),
                        3,
                    ),
                    (
                        TerminologyConcept.display_name.ilike(
                            f"%{normalized}%",
                        )
                        & TerminologyConcept.is_residual.is_(False),
                        4,
                    ),
                    (
                        TerminologyConcept.display_name.ilike(
                            f"%{normalized}%",
                        ),
                        5,
                    ),
                    (
                        synonym_prefix_match
                        & TerminologyConcept.is_residual.is_(False),
                        6,
                    ),
                    (
                        synonym_prefix_match,
                        7,
                    ),
                    (
                        synonym_match
                        & TerminologyConcept.is_residual.is_(False),
                        8,
                    ),
                    (
                        synonym_match,
                        9,
                    ),
                    else_=10,
                ),
                TerminologyConcept.display_name.asc(),
            )
            .limit(limit)
        )

        if system is not None:
            statement = statement.where(
                TerminologyConcept.system == system,
            )

        if leaf_only:
            statement = statement.where(
                TerminologyConcept.is_leaf.is_(True),
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
