from sqlalchemy.orm import Session

from app.modules.terminology.enums import TerminologySystem
from app.modules.terminology.models import (
    TerminologyConcept,
    TerminologySynonym,
)


DEV_DIAGNOSES = [
    {
        "system": TerminologySystem.ICD_10_CM,
        "code": "I10",
        "display_name": "Essential (primary) hypertension",
        "synonyms": [
            "Hypertension",
            "Primary hypertension",
        ],
    },
    {
        "system": TerminologySystem.ICD_10_CM,
        "code": "E11.9",
        "display_name": "Type 2 diabetes mellitus without complications",
        "synonyms": [
            "Type 2 diabetes",
            "T2DM",
            "Diabetes mellitus type 2",
        ],
    },
    {
        "system": TerminologySystem.ICD_10_CM,
        "code": "J45.909",
        "display_name": "Unspecified asthma, uncomplicated",
        "synonyms": [
            "Asthma",
            "Bronchial asthma",
        ],
    },
    {
        "system": TerminologySystem.ICD_10_CM,
        "code": "N80.9",
        "display_name": "Endometriosis, unspecified",
        "synonyms": [
            "Endometriosis",
        ],
    },
    {
        "system": TerminologySystem.ICD_10_CM,
        "code": "B50.9",
        "display_name": "Plasmodium malariae malaria, unspecified",
        "synonyms": [
            "Malaria",
        ],
    },
]


def seed_development_terminology(
    db: Session,
) -> None:
    """
    Seed a small development-only terminology fixture.

    This is not a production ICD-10-CM dataset.
    """

    for item in DEV_DIAGNOSES:
        concept = (
            db.query(TerminologyConcept)
            .filter(
                TerminologyConcept.system == item["system"],
                TerminologyConcept.code == item["code"],
            )
            .one_or_none()
        )

        if concept is None:
            concept = TerminologyConcept(
                system=item["system"],
                code=item["code"],
                display_name=item["display_name"],
                active=True,
            )

            db.add(concept)
            db.flush()

        existing_terms = {
            synonym.term
            for synonym in concept.synonyms
        }

        for term in item["synonyms"]:
            if term not in existing_terms:
                db.add(
                    TerminologySynonym(
                        concept_id=concept.id,
                        term=term,
                    )
                )

    db.commit()
