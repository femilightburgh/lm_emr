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
        release_version="TEST",
        is_leaf=True,
        is_residual=False,
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
        release_version="TEST",
        is_leaf=True,
        is_residual=False,
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


def test_search_excludes_non_leaf_concepts_by_default(
    db,
):
    leaf = seed_concept(
        db,
        display_name="Hypertensive disorder",
    )

    non_leaf = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=f"TEST-GROUP-{uuid4().hex[:8]}",
        display_name="Hypertensive diseases",
        active=True,
        release_version="TEST",
        is_leaf=False,
        is_residual=False,
    )

    db.add(non_leaf)
    db.commit()

    service = create_terminology_service(db)

    results = service.search(
        query="hypertensive",
    )

    assert [item.id for item in results] == [leaf.id]


def test_search_can_include_non_leaf_concepts(
    db,
):
    leaf = seed_concept(
        db,
        display_name="Hypertensive disorder",
    )

    non_leaf = TerminologyConcept(
        system=TerminologySystem.ICD_10_CM,
        code=f"TEST-GROUP-{uuid4().hex[:8]}",
        display_name="Hypertensive diseases",
        active=True,
        release_version="TEST",
        is_leaf=False,
        is_residual=False,
    )

    db.add(non_leaf)
    db.commit()

    service = create_terminology_service(db)

    results = service.search(
        query="hypertensive",
        leaf_only=False,
    )

    assert [item.id for item in results] == [
        non_leaf.id,
        leaf.id,
    ]


def test_search_prioritizes_exact_code_match(
    db,
):
    exact_code = seed_concept(
        db,
        code="HYPERTENSION",
        display_name="Essential hypertension, unspecified",
    )

    name_match = seed_concept(
        db,
        code="TEST-NAME",
        display_name="Hypertension",
    )

    service = create_terminology_service(db)

    results = service.search(
        query="HYPERTENSION",
    )

    assert [concept.id for concept in results[:2]] == [
        exact_code.id,
        name_match.id,
    ]


def test_search_prioritizes_query_at_start_of_name(
    db,
):
    starts_with_query = seed_concept(
        db,
        code="TEST-START",
        display_name="Hypertension due to endocrine disorder",
    )

    query_later = seed_concept(
        db,
        code="TEST-LATER",
        display_name="Chronic pulmonary hypertension",
    )

    service = create_terminology_service(db)

    results = service.search(
        query="hypertension",
    )

    assert [concept.id for concept in results[:2]] == [
        starts_with_query.id,
        query_later.id,
    ]


def test_search_prioritizes_non_residual_matches(
    db,
):
    non_residual = seed_concept(
        db,
        code="TEST-NON-RESIDUAL",
        display_name="Hypertension due to endocrine disorder",
    )

    residual = seed_concept(
        db,
        code="TEST-RESIDUAL",
        display_name="Hypertension, unspecified",
    )

    residual.is_residual = True
    db.flush()

    service = create_terminology_service(db)

    results = service.search(
        query="hypertension",
    )

    assert [concept.id for concept in results[:2]] == [
        non_residual.id,
        residual.id,
    ]


def test_search_prioritizes_exact_and_prefix_matches(
    db,
):
    exact = seed_concept(
        db,
        code="TEST-EXACT",
        display_name="Hypertension",
    )

    prefix = seed_concept(
        db,
        code="TEST-PREFIX",
        display_name="Hypertension due to endocrine disorder",
    )

    contains = seed_concept(
        db,
        code="TEST-CONTAINS",
        display_name="Pulmonary hypertension",
    )

    synonym = seed_concept(
        db,
        code="TEST-SYNONYM",
        display_name="Elevated blood pressure",
        synonyms=("Hypertension",),
    )

    service = create_terminology_service(db)

    results = service.search(
        query="hypertension",
    )

    assert [item.id for item in results] == [
        exact.id,
        prefix.id,
        contains.id,
        synonym.id,
    ]


def test_search_blank_query_returns_no_results(
    db,
):
    service = create_terminology_service(db)

    assert service.search(query="   ") == []
