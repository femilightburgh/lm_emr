"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Repository
==============================================================================

Provides persistence operations for Clinical Documents.

Business rules belong in ClinicalDocumentService.

==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clinical_documents.models import ClinicalDocument
from app.modules.episode.models import Episode
from app.modules.encounter.models import Encounter


class ClinicalDocumentRepository:
    """
    Repository for Clinical Document persistence.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # =========================================================================
    # Create
    # =========================================================================

    def create(
        self,
        *,
        document: ClinicalDocument,
    ) -> ClinicalDocument:
        """
        Add a Clinical Document to the current transaction.
        """

        self.db.add(document)

        return document

    # =========================================================================
    # Retrieve
    # =========================================================================

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        document_id: UUID,
    ) -> ClinicalDocument | None:
        """
        Retrieve a Clinical Document belonging to the authenticated Hospital.

        Hospital ownership is inherited through:

            ClinicalDocument
                ↓
            Encounter
                ↓
            Episode
                ↓
            Hospital
        """

        statement = (
            select(ClinicalDocument)
            .join(
                Encounter,
                ClinicalDocument.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalDocument.id == document_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # =========================================================================
    # Encounter Documents
    # =========================================================================

    def list_by_encounter(
        self,
        *,
        hospital_id: UUID,
        encounter_id: UUID,
    ) -> list[ClinicalDocument]:
        """
        Return all Clinical Documents belonging to an Encounter
        within the authenticated Hospital.
        """

        statement = (
            select(ClinicalDocument)
            .join(
                Encounter,
                ClinicalDocument.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalDocument.encounter_id == encounter_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalDocument.created_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Version History
    # =========================================================================

    def list_versions(
        self,
        *,
        hospital_id: UUID,
        encounter_id: UUID,
        document_type,
    ) -> list[ClinicalDocument]:
        """
        Return all versions of a document type for an Encounter.

        Versions are returned from oldest to newest.
        """

        statement = (
            select(ClinicalDocument)
            .join(
                Encounter,
                ClinicalDocument.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                Encounter.episode_id == Episode.id,
            )
            .where(
                ClinicalDocument.encounter_id == encounter_id,
                ClinicalDocument.document_type == document_type,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalDocument.version.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Persistence
    # =========================================================================

    def save(self) -> None:
        """
        Commit the current transaction.
        """

        self.db.commit()

    def refresh(
        self,
        document: ClinicalDocument,
    ) -> None:
        """
        Refresh a Clinical Document from the database.
        """

        self.db.refresh(document)