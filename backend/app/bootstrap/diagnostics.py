"""
==============================================================================
LIGHTBURGH EMR

Diagnostics Catalogue Bootstrap
==============================================================================
"""

from sqlalchemy.orm import Session

from app.modules.diagnostics.enums import DiagnosticCategory
from app.modules.diagnostics.models import DiagnosticInvestigation
from app.modules.diagnostics.repositories import DiagnosticRepository


DIAGNOSTIC_INVESTIGATION_CATALOGUE = [
    {
        "code": "XRAY",
        "name": "X-ray",
        "category": DiagnosticCategory.RADIOLOGY,
        "description": (
            "Plain radiographic imaging investigation."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "clinical_information",
                    "label": "Clinical Information",
                    "type": "TEXT",
                },
                {
                    "code": "technique",
                    "label": "Technique",
                    "type": "TEXT",
                },
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
                {
                    "code": "recommendations",
                    "label": "Recommendations",
                    "type": "TEXT",
                },
            ]
        },
    },
    {
        "code": "ULTRASOUND",
        "name": "Ultrasound",
        "category": DiagnosticCategory.RADIOLOGY,
        "description": (
            "Diagnostic ultrasound imaging investigation."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "clinical_information",
                    "label": "Clinical Information",
                    "type": "TEXT",
                },
                {
                    "code": "technique",
                    "label": "Technique",
                    "type": "TEXT",
                },
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
                {
                    "code": "recommendations",
                    "label": "Recommendations",
                    "type": "TEXT",
                },
            ]
        },
    },
    {
        "code": "CT",
        "name": "CT Scan",
        "category": DiagnosticCategory.RADIOLOGY,
        "description": (
            "Computed tomography imaging investigation."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "clinical_information",
                    "label": "Clinical Information",
                    "type": "TEXT",
                },
                {
                    "code": "technique",
                    "label": "Technique",
                    "type": "TEXT",
                },
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
                {
                    "code": "recommendations",
                    "label": "Recommendations",
                    "type": "TEXT",
                },
            ]
        },
    },
    {
        "code": "MRI",
        "name": "MRI",
        "category": DiagnosticCategory.RADIOLOGY,
        "description": (
            "Magnetic resonance imaging investigation."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "clinical_information",
                    "label": "Clinical Information",
                    "type": "TEXT",
                },
                {
                    "code": "technique",
                    "label": "Technique",
                    "type": "TEXT",
                },
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
                {
                    "code": "recommendations",
                    "label": "Recommendations",
                    "type": "TEXT",
                },
            ]
        },
    },
    {
        "code": "ECG",
        "name": "Electrocardiogram",
        "category": DiagnosticCategory.CARDIOLOGY,
        "description": (
            "Electrocardiographic investigation."
        ),
        "report_template": {
            "fields": [
                {
                    "code": "heart_rate",
                    "label": "Heart Rate",
                    "type": "NUMBER",
                    "unit": "bpm",
                },
                {
                    "code": "rhythm",
                    "label": "Rhythm",
                    "type": "TEXT",
                },
                {
                    "code": "pr_interval",
                    "label": "PR Interval",
                    "type": "NUMBER",
                    "unit": "ms",
                },
                {
                    "code": "qrs_duration",
                    "label": "QRS Duration",
                    "type": "NUMBER",
                    "unit": "ms",
                },
                {
                    "code": "qt_interval",
                    "label": "QT Interval",
                    "type": "NUMBER",
                    "unit": "ms",
                },
                {
                    "code": "qtc_interval",
                    "label": "QTc",
                    "type": "NUMBER",
                    "unit": "ms",
                },
                {
                    "code": "axis",
                    "label": "Axis",
                    "type": "TEXT",
                },
                {
                    "code": "st_t_changes",
                    "label": "ST/T Changes",
                    "type": "TEXT",
                },
            ],
            "sections": [
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "interpretation",
                    "label": "Interpretation",
                    "type": "TEXT",
                },
            ],
        },
    },
    {
        "code": "ECHO",
        "name": "Echocardiography",
        "category": DiagnosticCategory.CARDIOLOGY,
        "description": (
            "Cardiac ultrasound and echocardiographic investigation."
        ),
        "report_template": {
            "fields": [
                {
                    "code": "ejection_fraction",
                    "label": "Ejection Fraction",
                    "type": "NUMBER",
                    "unit": "%",
                },
                {
                    "code": "lv_size",
                    "label": "Left Ventricle",
                    "type": "TEXT",
                },
                {
                    "code": "rv_size",
                    "label": "Right Ventricle",
                    "type": "TEXT",
                },
                {
                    "code": "valves",
                    "label": "Valves",
                    "type": "TEXT",
                },
                {
                    "code": "wall_motion",
                    "label": "Wall Motion",
                    "type": "TEXT",
                },
                {
                    "code": "pericardium",
                    "label": "Pericardium",
                    "type": "TEXT",
                },
            ],
            "sections": [
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
            ],
        },
    },
    {
        "code": "EEG",
        "name": "Electroencephalography",
        "category": DiagnosticCategory.NEUROPHYSIOLOGY,
        "description": (
            "Electroencephalographic investigation."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "clinical_information",
                    "label": "Clinical Information",
                    "type": "TEXT",
                },
                {
                    "code": "background",
                    "label": "Background Activity",
                    "type": "TEXT",
                },
                {
                    "code": "activation",
                    "label": "Activation Procedures",
                    "type": "TEXT",
                },
                {
                    "code": "epileptiform_activity",
                    "label": "Epileptiform Activity",
                    "type": "TEXT",
                },
                {
                    "code": "other_findings",
                    "label": "Other Findings",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
            ]
        },
    },
    {
        "code": "PFT",
        "name": "Pulmonary Function Test",
        "category": DiagnosticCategory.RESPIRATORY,
        "description": (
            "Pulmonary function testing investigation."
        ),
        "report_template": {
            "fields": [
                {
                    "code": "fev1",
                    "label": "FEV1",
                    "type": "NUMBER",
                    "unit": "L",
                },
                {
                    "code": "fvc",
                    "label": "FVC",
                    "type": "NUMBER",
                    "unit": "L",
                },
                {
                    "code": "fev1_fvc",
                    "label": "FEV1/FVC",
                    "type": "NUMBER",
                    "unit": "%",
                },
                {
                    "code": "bronchodilator_response",
                    "label": "Bronchodilator Response",
                    "type": "TEXT",
                },
            ],
            "sections": [
                {
                    "code": "interpretation",
                    "label": "Interpretation",
                    "type": "TEXT",
                },
            ],
        },
    },
    {
        "code": "AUDIOMETRY",
        "name": "Audiometry",
        "category": DiagnosticCategory.AUDIOLOGY,
        "description": (
            "Hearing assessment using audiometric testing."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "right_ear",
                    "label": "Right Ear",
                    "type": "TEXT",
                },
                {
                    "code": "left_ear",
                    "label": "Left Ear",
                    "type": "TEXT",
                },
                {
                    "code": "speech_discrimination",
                    "label": "Speech Discrimination",
                    "type": "TEXT",
                },
                {
                    "code": "other_findings",
                    "label": "Other Findings",
                    "type": "TEXT",
                },
                {
                    "code": "interpretation",
                    "label": "Interpretation",
                    "type": "TEXT",
                },
            ]
        },
    },
    {
        "code": "ENDOSCOPY",
        "name": "Endoscopy",
        "category": DiagnosticCategory.ENDOSCOPY,
        "description": (
            "Endoscopic diagnostic examination."
        ),
        "report_template": {
            "sections": [
                {
                    "code": "indication",
                    "label": "Indication",
                    "type": "TEXT",
                },
                {
                    "code": "procedure",
                    "label": "Procedure",
                    "type": "TEXT",
                },
                {
                    "code": "extent",
                    "label": "Extent",
                    "type": "TEXT",
                },
                {
                    "code": "findings",
                    "label": "Findings",
                    "type": "TEXT",
                },
                {
                    "code": "specimens",
                    "label": "Specimens / Biopsies",
                    "type": "TEXT",
                },
                {
                    "code": "impression",
                    "label": "Impression",
                    "type": "TEXT",
                },
                {
                    "code": "recommendations",
                    "label": "Recommendations",
                    "type": "TEXT",
                },
            ]
        },
    },
]


def bootstrap_diagnostic_investigations(
    session: Session,
    hospital_id,
) -> None:
    """
    Synchronize the built-in Diagnostics catalogue.

    Existing entries are preserved. Missing entries are created.
    """

    repository = DiagnosticRepository(session)

    for definition in DIAGNOSTIC_INVESTIGATION_CATALOGUE:
        existing = repository.get_investigation_by_code(
            hospital_id=hospital_id,
            code=definition["code"],
        )

        if existing is not None:
            continue

        repository.create_investigation(
            investigation=DiagnosticInvestigation(
                hospital_id=hospital_id,
                **definition,
            ),
        )

    repository.save()
