from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.models import TerminologyConcept
from app.modules.terminology.repositories import TerminologyRepository


class TerminologyService:
    """
    Business service for terminology lookup.
    """

    def __init__(
        self,
        *,
        repository: TerminologyRepository,
    ) -> None:
        self.repository = repository

    def search(
        self,
        *,
        query: str,
        system: TerminologySystem | None = None,
        limit: int = 20,
    ) -> list[TerminologyConcept]:
        if limit < 1 or limit > 100:
            raise ValueError(
                "Terminology search limit must be between 1 and 100.",
            )

        return self.repository.search(
            query=query,
            system=system,
            limit=limit,
        )
