from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security.authorization import require_permission
from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.repositories import TerminologyRepository
from app.modules.terminology.schemas import TerminologyConceptResponse
from app.modules.terminology.services import TerminologyService
from app.modules.identity.permissions import Permissions


router = APIRouter(
    prefix="/terminology",
    tags=["Terminology"],
)


def get_terminology_service(
    db: Session = Depends(get_db),
) -> TerminologyService:
    return TerminologyService(
        repository=TerminologyRepository(db),
    )


@router.get(
    "/diagnoses/search",
    response_model=list[TerminologyConceptResponse],
    summary="Search Diagnosis Terminology",
    dependencies=[
        Depends(
            require_permission(
                Permissions.TERMINOLOGY_READ,
            ),
        ),
    ],
)
def search_diagnoses(
    q: str = Query(
        ...,
        min_length=1,
        max_length=200,
        description="Diagnosis name, synonym, or terminology code.",
    ),
    system: TerminologySystem | None = Query(
        default=None,
        description="Optional terminology system filter.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    service: TerminologyService = Depends(
        get_terminology_service,
    ),
):
    concepts = service.search(
        query=q,
        system=system,
        limit=limit,
    )

    return [
        TerminologyConceptResponse.model_validate(concept)
        for concept in concepts
    ]
