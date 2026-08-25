from uuid import uuid4

import pytest

from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.models import (
    TerminologyConcept,
    TerminologySynonym,
)
from app.modules.terminology.repositories import TerminologyRepository
from app.modules.terminology.services import TerminologyService


@pytest.fixture(autouse=True)
def clean_terminology(db):
    db.execute(TerminologySynonym.__table__.delete())
    db.execute(TerminologyConcept.__table__.delete())
    db.commit()


def create_terminology_service(db):
    return TerminologyService(
        repository=TerminologyRepository(db),
    )


def seed_concept(
    db,
    *,
    code=None,
    display_name,
    synonyms=(),
):
    code = code or f"TEST-{uuid4().hex[:12]}"

    concept = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=code,
        display_name=display_name,
        active=True,
    )

    db.add(concept)
    db.flush()

    for term in synonyms:
        db.add(
            TerminologySynonym(
                concept_id=concept.id,
                term=term,
            )
        )

    db.commit()
    db.refresh(concept)

    return concept


def test_search_matches_display_name(
    db,
):
    concept = seed_concept(
        db,
        display_name="Essential (primary) hypertension",
    )

    service = create_terminology_service(db)

    results = service.search(
        query="hypertension",
    )

    assert [item.id for item in results] == [concept.id]


def test_search_matches_code(
    db,
):
    concept = seed_concept(
        db,
        display_name="Essential (primary) hypertension",
    )

    service = create_terminology_service(db)

    results = service.search(
        query=concept.code,
    )

    assert [item.id for item in results] == [concept.id]


def test_search_matches_synonym(
    db,
):
    concept = seed_concept(
        db,
        display_name="Essential (primary) hypertension",
        synonyms=["Primary hypertension"],
    )

    service = create_terminology_service(db)

    results = service.search(
        query="primary hypertension",
    )

    assert [item.id for item in results] == [concept.id]


def test_search_can_filter_by_terminology_system(
    db,
):
    icd = seed_concept(
        db,
        display_name="Essential (primary) hypertension",
    )

    other = TerminologyConcept(
        system=TerminologySystem.SNOMED_CT,
        code="38341003",
        display_name="Hypertensive disorder",
        active=True,
    )

    db.add(other)
    db.commit()

    service = create_terminology_service(db)

    results = service.search(
        query="hypertension",
        system=TerminologySystem.ICD_10_CM,
    )

    assert [item.id for item in results] == [icd.id]


def test_search_excludes_inactive_concepts(
    db,
):
    concept = seed_concept(
        db,
        display_name="Essential (primary) hypertension",
    )

    concept.active = False
    db.commit()

    service = create_terminology_service(db)

    results = service.search(
        query="hypertension",
    )

    assert results == []


def test_search_blank_query_returns_no_results(
    db,
):
    service = create_terminology_service(db)

    assert service.search(query="   ") == []
