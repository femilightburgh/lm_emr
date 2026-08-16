"""
==============================================================================
LIGHTBURGH EMR

Clinical Document API Schema Tests
==============================================================================
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)

from app.modules.clinical_documents.schemas import (
    AmendClinicalDocumentRequest,
    ClinicalDocumentResponse,
    CreateClinicalDocumentRequest,
    SignClinicalDocumentRequest,
)


# ============================================================================
# Create Clinical Document Request
# ============================================================================


def test_create_clinical_document_request():
    request = CreateClinicalDocumentRequest(
        encounter_id=uuid4(),
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=uuid4(),
        content={
            "presenting_complaints": [
                {
                    "complaint": "Fever",
                    "duration": "3 days",
                },
            ],
            "history_of_presenting_complaint": (
                "Patient developed fever three days ago."
            ),
        },
    )

    assert request.document_type == (
        ClinicalDocumentType.INITIAL_CLERKING
    )

    assert len(request.content["presenting_complaints"]) == 1

    assert request.content["presenting_complaints"][0]["complaint"] == (
        "Fever"
    )


def test_create_clinical_document_request_validates_content():
    request = CreateClinicalDocumentRequest(
        encounter_id=uuid4(),
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        authored_by=uuid4(),
        content={
            "examination": {
                "general": "Conscious and alert.",
                "cardiovascular": "S1 and S2 heard.",
            },
            "assessment": {
                "working_diagnosis": "Malaria",
                "differentials": [
                    "Typhoid fever",
                ],
            },
        },
    )

    assert request.content["examination"]["general"] == (
        "Conscious and alert."
    )

    assert request.content["assessment"]["working_diagnosis"] == (
        "Malaria"
    )


# ============================================================================
# Sign Clinical Document Request
# ============================================================================


def test_sign_clinical_document_request():
    signed_at = datetime(
        2026,
        8,
        15,
        16,
        0,
        tzinfo=timezone.utc,
    )

    request = SignClinicalDocumentRequest(
        signed_by=uuid4(),
        signed_at=signed_at,
    )

    assert request.signed_at == signed_at


def test_sign_clinical_document_request_allows_missing_time():
    request = SignClinicalDocumentRequest(
        signed_by=uuid4(),
    )

    assert request.signed_at is None


# ============================================================================
# Amend Clinical Document Request
# ============================================================================


def test_amend_clinical_document_request():
    request = AmendClinicalDocumentRequest(
        authored_by=uuid4(),
        content={
            "history_of_presenting_complaint": "Updated history.",
            "examination": {
                "general": "Patient remains stable.",
            },
        },
    )

    assert request.content["history_of_presenting_complaint"] == (
        "Updated history."
    )

    assert request.content["examination"]["general"] == (
        "Patient remains stable."
    )


# ============================================================================
# Clinical Document Response
# ============================================================================


def test_clinical_document_response():
    document_id = uuid4()
    encounter_id = uuid4()
    authored_by = uuid4()

    response = ClinicalDocumentResponse(
        id=document_id,
        encounter_id=encounter_id,
        document_type=ClinicalDocumentType.INITIAL_CLERKING,
        status=ClinicalDocumentStatus.SIGNED,
        version=1,
        content={
            "history_of_presenting_complaint": "Patient is improving.",
        },
        authored_by=authored_by,
        signed_at=datetime(
            2026,
            8,
            15,
            16,
            0,
            tzinfo=timezone.utc,
        ),
        signed_by=authored_by,
        amended_from_id=None,
    )

    assert response.id == document_id
    assert response.encounter_id == encounter_id
    assert response.status == ClinicalDocumentStatus.SIGNED
    assert response.version == 1


# ============================================================================
# Progress Note
# ============================================================================


def test_create_request_validates_progress_note_content():
    request = CreateClinicalDocumentRequest(
        encounter_id=uuid4(),
        document_type=ClinicalDocumentType.PROGRESS_NOTE,
        authored_by=uuid4(),
        content={
            "subjective": "Patient feels better.",
            "objective": "Temperature normal.",
            "assessment": {
                "working_diagnosis": "Malaria",
            },
            "plan": "Continue treatment.",
        },
    )

    assert request.content["subjective"] == (
        "Patient feels better."
    )

    assert request.content["assessment"]["working_diagnosis"] == (
        "Malaria"
    )


# ============================================================================
# Discharge Summary
# ============================================================================


def test_create_request_validates_discharge_summary_content():
    request = CreateClinicalDocumentRequest(
        encounter_id=uuid4(),
        document_type=ClinicalDocumentType.DISCHARGE_SUMMARY,
        authored_by=uuid4(),
        content={
            "admission_summary": "Admitted with fever.",
            "hospital_course": "Improved with treatment.",
            "diagnoses": ["Malaria"],
            "condition_at_discharge": "Stable.",
        },
    )

    assert request.content["diagnoses"] == ["Malaria"]

    assert request.content["condition_at_discharge"] == (
        "Stable."
    )


# ============================================================================
# Invalid Document-Type Content
# ============================================================================


def test_create_request_rejects_invalid_content_for_document_type():
    with pytest.raises(ValidationError):
        CreateClinicalDocumentRequest(
            encounter_id=uuid4(),
            document_type=ClinicalDocumentType.PROGRESS_NOTE,
            authored_by=uuid4(),
            content={
                "presenting_complaints": [
                    {
                        "complaint": "Fever",
                        "duration": "3 days",
                    },
                ],
            },
        )