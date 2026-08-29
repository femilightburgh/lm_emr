"""
==============================================================================
LIGHTBURGH EMR

Laboratory Catalogue Bootstrap
==============================================================================
"""

from sqlalchemy.orm import Session

from app.modules.laboratory.enums import LaboratoryAnalyteDataType
from app.modules.laboratory.models import (
    LaboratoryTest,
    LaboratoryTestAnalyte,
)
from app.modules.laboratory.repositories import (
    LaboratoryTestRepository,
)


LABORATORY_TEST_CATALOGUE = [
    {
        "code": "CBC",
        "name": "Full Blood Count",
        "specimen": "EDTA blood",
        "description": (
            "Full blood count laboratory investigation."
        ),
        "analytes": [
            {
                "code": "hemoglobin",
                "name": "Haemoglobin",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "g/dL",
                "reference_low": 12,
                "reference_high": 16,
                "required": False,
                "display_order": 0,
            },
            {
                "code": "white_cell_count",
                "name": "White cell count",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "×10⁹/L",
                "required": False,
                "display_order": 1,
            },
            {
                "code": "neutrophils",
                "name": "Neutrophils",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "%",
                "required": False,
                "display_order": 2,
            },
            {
                "code": "lymphocytes",
                "name": "Lymphocytes",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "%",
                "required": False,
                "display_order": 3,
            },
            {
                "code": "platelets",
                "name": "Platelets",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "×10⁹/L",
                "required": False,
                "display_order": 4,
            },
        ],
    },
    {
        "code": "MALARIA",
        "name": "Malaria Test",
        "specimen": "Blood",
        "description": (
            "Laboratory investigation for malaria parasites."
        ),
        "analytes": [
            {
                "code": "parasite_detected",
                "name": "Parasite detected",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": [
                    "Positive",
                    "Negative",
                ],
                "required": False,
                "display_order": 0,
            },
            {
                "code": "species",
                "name": "Species",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": [
                    "P. falciparum",
                    "P. malariae",
                    "P. vivax",
                    "P. ovale",
                    "Mixed",
                    "Not identified",
                ],
                "required": False,
                "display_order": 1,
            },
            {
                "code": "parasite_density",
                "name": "Parasite density",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 2,
            },
        ],
    },
    {
        "code": "EUCR",
        "name": "Electrolytes, Urea and Creatinine",
        "specimen": "Serum",
        "description": (
            "Electrolytes, urea and creatinine laboratory investigation."
        ),
        "analytes": [
            {
                "code": "sodium",
                "name": "Sodium",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 0,
            },
            {
                "code": "potassium",
                "name": "Potassium",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 1,
            },
            {
                "code": "chloride",
                "name": "Chloride",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 2,
            },
            {
                "code": "bicarbonate",
                "name": "Bicarbonate",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 3,
            },
            {
                "code": "urea",
                "name": "Urea",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 4,
            },
            {
                "code": "creatinine",
                "name": "Creatinine",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "µmol/L",
                "required": False,
                "display_order": 5,
            },
        ],
    },
]


def bootstrap_laboratory_tests(
    session: Session,
    hospital_id,
) -> None:
    """
    Synchronize the built-in Laboratory Test catalogue.

    Existing catalogue entries are preserved. Missing tests and
    missing analytes are created. Running this function repeatedly
    is safe.
    """

    repository = LaboratoryTestRepository(session)

    for definition in LABORATORY_TEST_CATALOGUE:
        existing = repository.get_by_code(
            hospital_id=hospital_id,
            code=definition["code"],
        )

        if existing is None:
            existing = LaboratoryTest(
                hospital_id=hospital_id,
                code=definition["code"],
                name=definition["name"],
                specimen=definition["specimen"],
                description=definition["description"],
                active=True,
            )

            repository.create(
                laboratory_test=existing,
            )

            session.flush()

        existing_analyte_codes = {
            analyte.code.upper()
            for analyte in existing.analytes
        }

        for analyte_definition in definition["analytes"]:
            analyte_code = analyte_definition["code"].upper()

            if analyte_code in existing_analyte_codes:
                continue

            repository.create_analyte(
                analyte=LaboratoryTestAnalyte(
                    laboratory_test_id=existing.id,
                    code=analyte_definition["code"],
                    name=analyte_definition["name"],
                    data_type=analyte_definition["data_type"],
                    unit=analyte_definition.get("unit"),
                    reference_low=analyte_definition.get(
                        "reference_low"
                    ),
                    reference_high=analyte_definition.get(
                        "reference_high"
                    ),
                    reference_text=analyte_definition.get(
                        "reference_text"
                    ),
                    options=analyte_definition.get(
                        "options"
                    ),
                    required=bool(
                        analyte_definition.get(
                            "required",
                            False,
                        )
                    ),
                    display_order=analyte_definition.get(
                        "display_order",
                        0,
                    ),
                )
            )

        session.flush()
