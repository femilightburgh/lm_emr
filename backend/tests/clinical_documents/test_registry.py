"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Schema Registry Tests
==============================================================================
"""

import pytest

from app.modules.clinical_documents.enums import ClinicalDocumentType
from app.modules.clinical_documents.schemas import (
    DischargeSummaryContent,
    InitialClerkingContent,
    ProgressNoteContent,
    get_document_content_schema,
)


# ============================================================================
# Schema Mapping
# ============================================================================


def test_initial_clerking_maps_to_correct_schema():
    schema = get_document_content_schema(
        ClinicalDocumentType.INITIAL_CLERKING,
    )

    assert schema is InitialClerkingContent


def test_progress_note_maps_to_correct_schema():
    schema = get_document_content_schema(
        ClinicalDocumentType.PROGRESS_NOTE,
    )

    assert schema is ProgressNoteContent


def test_discharge_summary_maps_to_correct_schema():
    schema = get_document_content_schema(
        ClinicalDocumentType.DISCHARGE_SUMMARY,
    )

    assert schema is DischargeSummaryContent


# ============================================================================
# Registry Validation
# ============================================================================


def test_initial_clerking_content_is_validated_by_registry():
    schema = get_document_content_schema(
        ClinicalDocumentType.INITIAL_CLERKING,
    )

    content = schema(
        presenting_complaints=[
            {
                "complaint": "Fever",
                "duration": "3 days",
            },
        ],
    )

    assert isinstance(content, InitialClerkingContent)


def test_progress_note_content_is_validated_by_registry():
    schema = get_document_content_schema(
        ClinicalDocumentType.PROGRESS_NOTE,
    )

    content = schema(
        subjective="Patient feels better.",
        objective="Temperature has normalized.",
        assessment={
            "working_diagnosis": "Malaria",
        },
        plan="Continue treatment.",
    )

    assert isinstance(content, ProgressNoteContent)


def test_discharge_summary_content_is_validated_by_registry():
    schema = get_document_content_schema(
        ClinicalDocumentType.DISCHARGE_SUMMARY,
    )

    content = schema(
        admission_summary="Admitted with fever.",
        hospital_course="Improved with treatment.",
        diagnoses=["Malaria"],
        discharge_medications=[
            "Artemether-lumefantrine",
        ],
        condition_at_discharge="Stable.",
        follow_up_plan="Review in one week.",
    )

    assert isinstance(content, DischargeSummaryContent)


# ============================================================================
# Invalid Document Type
# ============================================================================


def test_registry_rejects_unknown_document_type():
    with pytest.raises(ValueError):
        get_document_content_schema(
            "UNKNOWN_DOCUMENT_TYPE",
        )