"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Model
==============================================================================

A Clinical Document represents clinical documentation recorded during
an Encounter.

Examples include:

    • Initial clerking
    • Progress note
    • Discharge summary

Clinical Documents are versioned.

A signed version is immutable. When a clinician amends a signed document,
a new version is created and linked to the previous version through
``amended_from_id``.

Lifecycle
--------

    DRAFT
      |
      | sign
      v
    SIGNED
      |
      | amend
      v
    NEW DRAFT VERSION
      |
      | sign
      v
    SIGNED

Every signed version may generate a Clinical Event with:

    event_type = CLINICAL_NOTE_RECORDED

The Clinical Event records that the document version became part of
the clinical record. The Clinical Document contains the actual
clinical documentation.

==============================================================================
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)


if TYPE_CHECKING:
    from app.modules.encounter.models import Encounter
    from app.modules.staff.models import Staff


class ClinicalDocument(BaseEntity):
    """
    Represents one immutable version of a clinical document.

    A signed document must never be modified in place.

    Amendments create a new ClinicalDocument row with an incremented
    version and ``amended_from_id`` pointing to the previous version.
    """

    __tablename__ = "clinical_documents"

    __table_args__ = (
        UniqueConstraint(
            "encounter_id",
            "document_type",
            "version",
            name="uq_clinical_documents_encounter_type_version",
        ),
    )

    # =========================================================================
    # Encounter
    # =========================================================================

    encounter_id: Mapped[UUID] = mapped_column(
        ForeignKey("encounters.id"),
        nullable=False,
        index=True,
    )

    # =========================================================================
    # Document Information
    # =========================================================================

    document_type: Mapped[ClinicalDocumentType] = mapped_column(
        SqlEnum(
            ClinicalDocumentType,
            name="clinical_document_type_enum",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[ClinicalDocumentStatus] = mapped_column(
        SqlEnum(
            ClinicalDocumentStatus,
            name="clinical_document_status_enum",
        ),
        nullable=False,
        default=ClinicalDocumentStatus.DRAFT,
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # =========================================================================
    # Clinical Content
    # =========================================================================

    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # =========================================================================
    # Authorship
    # =========================================================================

    authored_by: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    # =========================================================================
    # Signing
    # =========================================================================

    signed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    signed_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True,
        index=True,
    )

    # =========================================================================
    # Version History
    # =========================================================================

    amended_from_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("clinical_documents.id"),
        nullable=True,
        index=True,
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    encounter: Mapped["Encounter"] = relationship(
        back_populates="clinical_documents",
    )

    author: Mapped["Staff"] = relationship(
        foreign_keys=[authored_by],
    )

    signer: Mapped["Staff | None"] = relationship(
        foreign_keys=[signed_by],
    )

    amended_from: Mapped["ClinicalDocument | None"] = relationship(
        remote_side="ClinicalDocument.id",
        foreign_keys=[amended_from_id],
    )