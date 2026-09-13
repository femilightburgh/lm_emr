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
    {
        "code": "ESR",
        "name": "Erythrocyte Sedimentation Rate",
        "specimen": "EDTA blood",
        "description": (
            "Erythrocyte sedimentation rate."
        ),
        "analytes": [
            {
                "code": "esr",
                "name": "ESR",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mm/hr",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "BGRH",
        "name": "Blood Group & Rh",
        "specimen": "EDTA blood",
        "description": (
            "ABO blood grouping and Rhesus typing."
        ),
        "analytes": [
            {
                "code": "abo_group",
                "name": "ABO group",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["A", "B", "AB", "O"],
                "required": False,
                "display_order": 0,
            },
            {
                "code": "rh_type",
                "name": "Rh type",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["Positive", "Negative"],
                "required": False,
                "display_order": 1,
            },
        ],
    },
    {
        "code": "RBCF",
        "name": "Peripheral Blood Film",
        "specimen": "EDTA blood",
        "description": (
            "Microscopic examination of a peripheral blood film."
        ),
        "analytes": [
            {
                "code": "blood_film",
                "name": "Blood film findings",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "RGLU",
        "name": "Random Blood Glucose",
        "specimen": "Fluoride plasma",
        "description": (
            "Random blood glucose measurement."
        ),
        "analytes": [
            {
                "code": "glucose",
                "name": "Glucose",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "FGLU",
        "name": "Fasting Blood Glucose",
        "specimen": "Fluoride plasma",
        "description": (
            "Fasting blood glucose measurement."
        ),
        "analytes": [
            {
                "code": "glucose",
                "name": "Glucose",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "HBA1C",
        "name": "HbA1c",
        "specimen": "EDTA blood",
        "description": (
            "Glycated haemoglobin measurement."
        ),
        "analytes": [
            {
                "code": "hba1c",
                "name": "HbA1c",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "%",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "LFT",
        "name": "Liver Function Test",
        "specimen": "Serum",
        "description": (
            "Liver biochemical profile."
        ),
        "analytes": [
            {
                "code": "alt",
                "name": "ALT",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "U/L",
                "required": False,
                "display_order": 0,
            },
            {
                "code": "ast",
                "name": "AST",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "U/L",
                "required": False,
                "display_order": 1,
            },
            {
                "code": "alp",
                "name": "Alkaline phosphatase",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "U/L",
                "required": False,
                "display_order": 2,
            },
            {
                "code": "total_bilirubin",
                "name": "Total bilirubin",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "µmol/L",
                "required": False,
                "display_order": 3,
            },
            {
                "code": "direct_bilirubin",
                "name": "Direct bilirubin",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "µmol/L",
                "required": False,
                "display_order": 4,
            },
            {
                "code": "albumin",
                "name": "Albumin",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "g/L",
                "required": False,
                "display_order": 5,
            },
            {
                "code": "total_protein",
                "name": "Total protein",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "g/L",
                "required": False,
                "display_order": 6,
            },
        ],
    },
    {
        "code": "LIPID",
        "name": "Lipid Profile",
        "specimen": "Serum",
        "description": (
            "Serum lipid profile."
        ),
        "analytes": [
            {
                "code": "total_cholesterol",
                "name": "Total cholesterol",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 0,
            },
            {
                "code": "hdl_cholesterol",
                "name": "HDL cholesterol",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 1,
            },
            {
                "code": "ldl_cholesterol",
                "name": "LDL cholesterol",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 2,
            },
            {
                "code": "triglycerides",
                "name": "Triglycerides",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 3,
            },
        ],
    },
    {
        "code": "CA",
        "name": "Calcium",
        "specimen": "Serum",
        "description": (
            "Serum calcium measurement."
        ),
        "analytes": [
            {
                "code": "calcium",
                "name": "Calcium",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "MG",
        "name": "Magnesium",
        "specimen": "Serum",
        "description": (
            "Serum magnesium measurement."
        ),
        "analytes": [
            {
                "code": "magnesium",
                "name": "Magnesium",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mmol/L",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "UA",
        "name": "Urinalysis",
        "specimen": "Urine",
        "description": (
            "Routine urine physical, chemical and microscopic examination."
        ),
        "analytes": [
            {
                "code": "appearance",
                "name": "Appearance",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 0,
            },
            {
                "code": "specific_gravity",
                "name": "Specific gravity",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "required": False,
                "display_order": 1,
            },
            {
                "code": "ph",
                "name": "pH",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "required": False,
                "display_order": 2,
            },
            {
                "code": "protein",
                "name": "Protein",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "required": False,
                "display_order": 3,
            },
            {
                "code": "glucose",
                "name": "Glucose",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "required": False,
                "display_order": 4,
            },
            {
                "code": "blood",
                "name": "Blood",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "required": False,
                "display_order": 5,
            },
            {
                "code": "leukocytes",
                "name": "Leukocytes",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["Negative", "Trace", "1+", "2+", "3+"],
                "required": False,
                "display_order": 6,
            },
            {
                "code": "nitrite",
                "name": "Nitrite",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": ["Positive", "Negative"],
                "required": False,
                "display_order": 7,
            },
            {
                "code": "microscopy",
                "name": "Microscopy",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 8,
            },
        ],
    },
    {
        "code": "UCS",
        "name": "Urine Culture & Sensitivity",
        "specimen": "Midstream urine",
        "description": (
            "Urine culture with antimicrobial susceptibility testing."
        ),
        "analytes": [
            {
                "code": "culture_result",
                "name": "Culture result",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 0,
            },
            {
                "code": "organism",
                "name": "Organism",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 1,
            },
            {
                "code": "sensitivity",
                "name": "Antimicrobial sensitivity",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 2,
            },
        ],
    },
    {
        "code": "BCS",
        "name": "Blood Culture & Sensitivity",
        "specimen": "Blood",
        "description": (
            "Blood culture with antimicrobial susceptibility testing."
        ),
        "analytes": [
            {
                "code": "culture_result",
                "name": "Culture result",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 0,
            },
            {
                "code": "organism",
                "name": "Organism",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 1,
            },
            {
                "code": "sensitivity",
                "name": "Antimicrobial sensitivity",
                "data_type": LaboratoryAnalyteDataType.TEXT,
                "required": False,
                "display_order": 2,
            },
        ],
    },
    {
        "code": "PTINR",
        "name": "Prothrombin Time / INR",
        "specimen": "Citrated plasma",
        "description": (
            "Prothrombin time and international normalized ratio."
        ),
        "analytes": [
            {
                "code": "pt",
                "name": "Prothrombin time",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "seconds",
                "required": False,
                "display_order": 0,
            },
            {
                "code": "inr",
                "name": "INR",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "required": False,
                "display_order": 1,
            },
        ],
    },
    {
        "code": "APTT",
        "name": "Activated Partial Thromboplastin Time",
        "specimen": "Citrated plasma",
        "description": (
            "Activated partial thromboplastin time."
        ),
        "analytes": [
            {
                "code": "aptt",
                "name": "aPTT",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "seconds",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "TSH",
        "name": "Thyroid Stimulating Hormone",
        "specimen": "Serum",
        "description": (
            "Thyroid stimulating hormone measurement."
        ),
        "analytes": [
            {
                "code": "tsh",
                "name": "TSH",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "mIU/L",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "FT4",
        "name": "Free T4",
        "specimen": "Serum",
        "description": (
            "Free thyroxine measurement."
        ),
        "analytes": [
            {
                "code": "free_t4",
                "name": "Free T4",
                "data_type": LaboratoryAnalyteDataType.NUMERIC,
                "unit": "pmol/L",
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "HIV",
        "name": "HIV Screening",
        "specimen": "Serum",
        "description": (
            "HIV screening investigation."
        ),
        "analytes": [
            {
                "code": "hiv_screen",
                "name": "HIV screening result",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": [
                    "Reactive",
                    "Non-reactive",
                    "Indeterminate",
                ],
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "HBSAG",
        "name": "Hepatitis B Surface Antigen",
        "specimen": "Serum",
        "description": (
            "Hepatitis B surface antigen screening."
        ),
        "analytes": [
            {
                "code": "hbsag",
                "name": "HBsAg",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": [
                    "Reactive",
                    "Non-reactive",
                    "Indeterminate",
                ],
                "required": False,
                "display_order": 0,
            },
        ],
    },
    {
        "code": "HCV",
        "name": "Hepatitis C Antibody",
        "specimen": "Serum",
        "description": (
            "Hepatitis C antibody screening."
        ),
        "analytes": [
            {
                "code": "hcv_antibody",
                "name": "HCV antibody",
                "data_type": LaboratoryAnalyteDataType.CODED,
                "options": [
                    "Reactive",
                    "Non-reactive",
                    "Indeterminate",
                ],
                "required": False,
                "display_order": 0,
            },
        ],
    }

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
