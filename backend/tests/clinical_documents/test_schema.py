"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Schema Tests
==============================================================================

Tests validation and serialization of structured Clinical Document content.
==============================================================================
"""

import pytest
from pydantic import ValidationError

from app.modules.clinical_documents.schemas import (
    Assessment,
    Examination,
    InitialClerkingContent,
    PatientPerspective,
    PresentingComplaint,
)


# ============================================================================
# Presenting Complaint
# ============================================================================


def test_presenting_complaint():
    complaint = PresentingComplaint(
        complaint="Fever",
        duration="3 days",
    )

    assert complaint.complaint == "Fever"
    assert complaint.duration == "3 days"


def test_presenting_complaint_requires_complaint():
    with pytest.raises(ValidationError):
        PresentingComplaint(
            complaint="",
            duration="3 days",
        )


def test_presenting_complaint_requires_duration():
    with pytest.raises(ValidationError):
        PresentingComplaint(
            complaint="Fever",
            duration="",
        )


# ============================================================================
# Patient Perspective
# ============================================================================


def test_patient_perspective():
    perspective = PatientPerspective(
        ideas="I think it is malaria.",
        concerns="I am worried about the fever.",
        expectations="I expect treatment today.",
    )

    assert perspective.ideas == "I think it is malaria."
    assert perspective.concerns == "I am worried about the fever."
    assert perspective.expectations == "I expect treatment today."


def test_patient_perspective_is_optional():
    perspective = PatientPerspective()

    assert perspective.ideas is None
    assert perspective.concerns is None
    assert perspective.expectations is None


# ============================================================================
# Examination
# ============================================================================


def test_examination_supports_narrative_sections():
    examination = Examination(
        general="Conscious and alert.",
        cardiovascular="S1 and S2 heard.",
        respiratory="Good air entry bilaterally.",
        abdomen="Soft and non-tender.",
        neurological="No focal neurological deficit.",
    )

    assert examination.general == "Conscious and alert."
    assert examination.cardiovascular == "S1 and S2 heard."
    assert examination.respiratory == "Good air entry bilaterally."
    assert examination.abdomen == "Soft and non-tender."
    assert examination.neurological == (
        "No focal neurological deficit."
    )


def test_examination_sections_are_optional():
    examination = Examination()

    assert examination.general is None
    assert examination.cardiovascular is None
    assert examination.respiratory is None
    assert examination.abdomen is None
    assert examination.neurological is None


# ============================================================================
# Assessment
# ============================================================================


def test_assessment_supports_working_diagnosis_and_differentials():
    assessment = Assessment(
        working_diagnosis="Malaria",
        differentials=[
            "Typhoid fever",
            "Viral infection",
        ],
    )

    assert assessment.working_diagnosis == "Malaria"
    assert assessment.differentials == [
        "Typhoid fever",
        "Viral infection",
    ]


def test_assessment_differentials_default_to_empty_list():
    assessment = Assessment(
        working_diagnosis="Malaria",
    )

    assert assessment.differentials == []


# ============================================================================
# Initial Clerking
# ============================================================================


def test_initial_clerking_supports_complete_core_structure():
    clerking = InitialClerkingContent(
        presenting_complaints=[
            {
                "complaint": "Fever",
                "duration": "3 days",
            },
            {
                "complaint": "Headache",
                "duration": "2 days",
            },
        ],
        history_of_presenting_complaint=(
            "Patient developed fever three days ago."
        ),
        review_of_systems="No cough, chest pain or vomiting.",
        past_medical_history="No known chronic illness.",
        past_surgical_history="No previous surgery.",
        drug_history="Not on regular medication.",
        allergies="No known drug allergy.",
        family_history="No significant family history.",
        social_history="Does not smoke or drink alcohol.",
        personal_history="Independent in activities of daily living.",
        patient_perspective={
            "ideas": "Thinks it is malaria.",
            "concerns": "Concerned about persistent fever.",
            "expectations": "Expects treatment.",
        },
        examination={
            "general": "Conscious and alert.",
            "cardiovascular": "S1 and S2 heard.",
            "respiratory": "Good air entry bilaterally.",
            "abdomen": "Soft and non-tender.",
        },
        assessment={
            "working_diagnosis": "Malaria",
            "differentials": [
                "Typhoid fever",
                "Viral infection",
            ],
        },
        investigations=[
            "Malaria parasite test",
            "Full blood count",
        ],
        plan="Treat according to investigation results.",
    )

    assert len(clerking.presenting_complaints) == 2
    assert (
        clerking.presenting_complaints[0].complaint
        == "Fever"
    )

    assert clerking.history_of_presenting_complaint == (
        "Patient developed fever three days ago."
    )

    assert clerking.patient_perspective.ideas == (
        "Thinks it is malaria."
    )

    assert clerking.examination.general == (
        "Conscious and alert."
    )

    assert clerking.assessment.working_diagnosis == "Malaria"

    assert clerking.investigations == [
        "Malaria parasite test",
        "Full blood count",
    ]


def test_initial_clerking_allows_context_dependent_sections_to_be_omitted():
    clerking = InitialClerkingContent(
        presenting_complaints=[
            {
                "complaint": "Fever",
                "duration": "3 days",
            },
        ],
    )

    assert clerking.gynaecological_history is None
    assert clerking.obstetric_history is None
    assert clerking.menstrual_history is None
    assert clerking.sexual_history is None


def test_initial_clerking_defaults_lists_to_empty():
    clerking = InitialClerkingContent()

    assert clerking.presenting_complaints == []
    assert clerking.investigations == []


# ============================================================================
# Serialization
# ============================================================================


def test_initial_clerking_serializes_to_json_compatible_dict():
    clerking = InitialClerkingContent(
        presenting_complaints=[
            {
                "complaint": "Fever",
                "duration": "3 days",
            },
        ],
        examination={
            "general": "Conscious and alert.",
        },
        assessment={
            "working_diagnosis": "Malaria",
        },
    )

    data = clerking.model_dump()

    assert data["presenting_complaints"] == [
        {
            "complaint": "Fever",
            "duration": "3 days",
        },
    ]

    assert data["examination"]["general"] == (
        "Conscious and alert."
    )

    assert data["assessment"]["working_diagnosis"] == "Malaria"


# ============================================================================
# Invalid Nested Data
# ============================================================================


def test_initial_clerking_rejects_invalid_presenting_complaint():
    with pytest.raises(ValidationError):
        InitialClerkingContent(
            presenting_complaints=[
                {
                    "complaint": "",
                    "duration": "3 days",
                },
            ],
        )