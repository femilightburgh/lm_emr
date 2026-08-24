"""
==============================================================================
LIGHTBURGH EMR

Clinical Document Service
==============================================================================

Business logic for Clinical Documents.

Clinical Document lifecycle:

    DRAFT
      |
      | edit
      v
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

MVP invariants
--------------

1. Clinical Documents belong to Encounters.
2. Encounters must belong to the authenticated Hospital.
3. Authors/signers must belong to the authenticated Hospital.
4. Clinical Documents cannot be created on CLOSED Encounters.
5. Only DRAFT documents may be edited.
6. SIGNED documents are immutable.
7. Only SIGNED documents may be amended.
8. Only the latest version may be amended.
9. Amendments create a new DRAFT version.
10. A DISCHARGE_SUMMARY requires an ADMITTED Episode.
11. Only the Episode managing doctor may sign a DISCHARGE_SUMMARY.
12. Signing creates the corresponding Clinical Event atomically.

Persistence belongs to repositories.

HTTP concerns belong to the API router.

==============================================================================
"""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel

from app.core.context import RequestContext

from app.modules.clinical_documents.enums import (
    ClinicalDocumentStatus,
    ClinicalDocumentType,
)

from app.modules.clinical_documents.exceptions import (
    ClinicalDocumentNotFoundError,
    ClinicalDocumentNotLatestVersionError,
    DocumentNotDraftError,
    DocumentNotSignedError,
    EncounterClosedError,
    EncounterNotFoundError,
    EpisodeNotAdmittedError,
    NotManagingDoctorError,
    StaffHospitalMismatchError,
    StaffNotFoundError,
)

from app.modules.clinical_documents.models import ClinicalDocument

from app.modules.clinical_documents.repositories import (
    ClinicalDocumentRepository,
)

from app.modules.encounter.models import EncounterStatus
from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)

from app.modules.episode.models import EpisodeStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)

from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.staff.repository import StaffRepository


class ClinicalDocumentService:
    """
    Business logic for Clinical Documents.
    """

    def __init__(
        self,
        *,
        repository: ClinicalDocumentRepository,
        event_service: ClinicalEventService,
    ) -> None:
        self.repository = repository

        self.encounter_repository = EncounterRepository(
            repository.db,
        )

        self.episode_repository = EpisodeRepository(
            repository.db,
        )

        self.staff_repository = StaffRepository(
            repository.db,
        )

        self.event_service = event_service

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _get_encounter(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ):
        """
        Retrieve an Encounter belonging to the authenticated Hospital.
        """

        encounter = self.encounter_repository.get_by_id(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

        if encounter is None:
            raise EncounterNotFoundError(
                "Encounter not found.",
            )

        return encounter

    def _validate_encounter_is_open(
        self,
        encounter,
    ) -> None:
        """
        Ensure the Encounter is still open for documentation.
        """

        if encounter.status != EncounterStatus.OPEN:
            raise EncounterClosedError(
                "Clinical Documents cannot be created on a closed Encounter.",
            )

    def _get_episode_for_encounter(
        self,
        *,
        context: RequestContext,
        encounter,
    ):
        """
        Retrieve the Episode associated with an Encounter.
        """

        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=encounter.episode_id,
        )

        if episode is None:
            raise EncounterNotFoundError(
                "Encounter Episode not found.",
            )

        return episode

    def _validate_discharge_summary_episode(
        self,
        *,
        context: RequestContext,
        encounter,
        document_type: ClinicalDocumentType,
    ):
        """
        Ensure a Discharge Summary is only created for an admitted Episode.

        Other Clinical Document types do not require an admitted Episode.
        """

        episode = self._get_episode_for_encounter(
            context=context,
            encounter=encounter,
        )

        if document_type != ClinicalDocumentType.DISCHARGE_SUMMARY:
            return episode

        if episode.status != EpisodeStatus.ADMITTED:
            raise EpisodeNotAdmittedError(
                "A Discharge Summary can only be created for an admitted Episode.",
            )

        return episode

    def _get_staff(
        self,
        *,
        context: RequestContext,
        staff_id: UUID,
    ):
        """
        Retrieve a Staff member by Staff ID and enforce Hospital ownership.

        This helper is appropriate when the caller genuinely supplies a
        Staff.id.
        """

        staff = self.staff_repository.get_by_id(
            staff_id,
        )

        if staff is None:
            raise StaffNotFoundError(
                "Staff member not found.",
            )

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError(
                "Staff member belongs to another Hospital.",
            )

        return staff

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        """
        Resolve the authenticated UserAccount to its Staff profile.

        RequestContext.user_id is a UserAccount.id, not a Staff.id.

        Therefore authenticated clinical operations must resolve the Staff
        record through Staff.user_account_id.
        """

        staff = self.staff_repository.get_by_user_account_id(
            hospital_id=context.hospital_id,
            user_account_id=context.user_id,
        )

        if staff is None:
            raise StaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError(
                "Staff member belongs to another Hospital.",
            )

        return staff

    # =========================================================================
    # Create Draft
    # =========================================================================

    def create_draft(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
        document_type: ClinicalDocumentType,
        authored_by: UUID,
        content: BaseModel | dict,
    ) -> ClinicalDocument:
        """
        Create a new Clinical Document in DRAFT status.

        The authenticated user's Staff profile is used as the author.

        The authored_by argument remains part of the service contract for
        compatibility with the API layer, but authorship is resolved from
        the authenticated RequestContext to prevent users from impersonating
        another Staff member.
        """

        encounter = self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        self._validate_encounter_is_open(
            encounter,
        )

        self._validate_discharge_summary_episode(
            context=context,
            encounter=encounter,
            document_type=document_type,
        )

        author = self._get_authenticated_staff(
            context=context,
        )

        if isinstance(content, BaseModel):
            content_data = content.model_dump(
                mode="json",
            )
        else:
            content_data = content

        versions = self.repository.list_versions(
            hospital_id=context.hospital_id,
            encounter_id=encounter.id,
            document_type=document_type,
        )

        if versions:
            next_version = max(
                document.version
                for document in versions
            ) + 1
        else:
            next_version = 1

        document = ClinicalDocument(
            encounter_id=encounter.id,
            document_type=document_type,
            status=ClinicalDocumentStatus.DRAFT,
            version=next_version,
            content=content_data,
            authored_by=author.id,
        )

        self.repository.create(
            document=document,
        )

        self.repository.save()
        self.repository.refresh(document)

        return document

    # =========================================================================
    # Retrieve
    # =========================================================================

    def get_document(
        self,
        *,
        context: RequestContext,
        document_id: UUID,
    ) -> ClinicalDocument:
        """
        Retrieve a Clinical Document belonging to the authenticated Hospital.
        """

        document = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            document_id=document_id,
        )

        if document is None:
            raise ClinicalDocumentNotFoundError(
                "Clinical Document not found.",
            )

        return document

    # =========================================================================
    # List Encounter Documents
    # =========================================================================

    def list_encounter_documents(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> list[ClinicalDocument]:
        """
        List all Clinical Documents belonging to an Encounter.
        """

        self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        return self.repository.list_by_encounter(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
        )

    # =========================================================================
    # List Versions
    # =========================================================================

    def list_versions(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
        document_type: ClinicalDocumentType,
    ) -> list[ClinicalDocument]:
        """
        Return all versions of a Clinical Document type for an Encounter.
        """

        self._get_encounter(
            context=context,
            encounter_id=encounter_id,
        )

        return self.repository.list_versions(
            hospital_id=context.hospital_id,
            encounter_id=encounter_id,
            document_type=document_type,
        )

    # =========================================================================
    # Update Draft
    # =========================================================================

    def update_draft(
        self,
        *,
        context: RequestContext,
        document_id: UUID,
        edited_by: UUID,
        content: BaseModel | dict,
    ) -> ClinicalDocument:
        """
        Update an existing DRAFT.

        Signed documents cannot be edited.

        The editor is resolved from the authenticated RequestContext.
        The edited_by argument remains in the method signature for API
        compatibility, but it is not trusted as a Staff.id.
        """

        document = self.get_document(
            context=context,
            document_id=document_id,
        )

        if document.status != ClinicalDocumentStatus.DRAFT:
            raise DocumentNotDraftError(
                "Only draft Clinical Documents can be edited.",
            )

        # RequestContext.user_id identifies UserAccount, not Staff.
        # Resolve the authenticated Staff profile correctly.
        editor = self._get_authenticated_staff(
            context=context,
        )

        if isinstance(content, BaseModel):
            content_data = content.model_dump(
                mode="json",
            )
        else:
            content_data = content

        document.content = content_data

        self.repository.save()
        self.repository.refresh(document)

        return document

    # =========================================================================
    # Sign
    # =========================================================================

    def sign_document(
        self,
        *,
        context: RequestContext,
        document_id: UUID,
        signed_at: datetime | None = None,
    ) -> ClinicalDocument:
        """
        Sign a Clinical Document.

        Only DRAFT documents can be signed.

        The signer is resolved from the authenticated RequestContext.

        Additional Discharge Summary rule:

            Only the Episode managing doctor may sign a
            DISCHARGE_SUMMARY.
        """

        document = self.get_document(
            context=context,
            document_id=document_id,
        )

        if document.status != ClinicalDocumentStatus.DRAFT:
            raise DocumentNotDraftError(
                "Only draft Clinical Documents can be signed.",
            )

        # RequestContext.user_id is UserAccount.id.
        signer = self._get_authenticated_staff(
            context=context,
        )

        # ------------------------------------------------------------------
        # Discharge Summary managing-doctor rule
        # ------------------------------------------------------------------

        if (
            document.document_type
            == ClinicalDocumentType.DISCHARGE_SUMMARY
        ):
            encounter = self._get_encounter(
                context=context,
                encounter_id=document.encounter_id,
            )

            episode = self._get_episode_for_encounter(
                context=context,
                encounter=encounter,
            )

            if episode.status != EpisodeStatus.ADMITTED:
                raise EpisodeNotAdmittedError(
                    "A Discharge Summary can only be signed for an admitted Episode.",
                )

            if episode.managing_doctor_id != signer.id:
                raise NotManagingDoctorError(
                    "Only the Episode managing doctor can sign the Discharge Summary.",
                )

        if signed_at is None:
            signed_at = datetime.now(timezone.utc)

        try:
            document.status = ClinicalDocumentStatus.SIGNED
            document.signed_at = signed_at
            document.signed_by = signer.id

            self.repository.db.flush()

            self.event_service.create_event(
                context=context,
                encounter_id=document.encounter_id,
                event_type=EventType.CLINICAL_NOTE_RECORDED,
                performed_by=signer.id,
                occurred_at=signed_at,
                payload={
                    "clinical_document_id": str(document.id),
                    "document_type": document.document_type.value,
                    "version": document.version,
                },
                commit=False,
            )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(document)

        return document

    # =========================================================================
    # Amend
    # =========================================================================

    def amend_document(
        self,
        *,
        context: RequestContext,
        document_id: UUID,
        authored_by: UUID,
        content: BaseModel | dict,
    ) -> ClinicalDocument:
        """
        Create a new DRAFT version from a SIGNED document.

        Only the latest version may be amended.

        The authenticated user's Staff profile becomes the author of the
        amended document.
        """

        document = self.get_document(
            context=context,
            document_id=document_id,
        )

        if document.status != ClinicalDocumentStatus.SIGNED:
            raise DocumentNotSignedError(
                "Only signed Clinical Documents can be amended.",
            )

        versions = self.repository.list_versions(
            hospital_id=context.hospital_id,
            encounter_id=document.encounter_id,
            document_type=document.document_type,
        )

        if not versions:
            raise ClinicalDocumentNotFoundError(
                "Clinical Document version history not found.",
            )

        latest_document = max(
            versions,
            key=lambda version: version.version,
        )

        if latest_document.id != document.id:
            raise ClinicalDocumentNotLatestVersionError(
                "Only the latest Clinical Document version can be amended.",
            )

        # Resolve the authenticated Staff correctly.
        author = self._get_authenticated_staff(
            context=context,
        )

        if isinstance(content, BaseModel):
            content_data = content.model_dump(
                mode="json",
            )
        else:
            content_data = content

        amended_document = ClinicalDocument(
            encounter_id=document.encounter_id,
            document_type=document.document_type,
            status=ClinicalDocumentStatus.DRAFT,
            version=document.version + 1,
            content=content_data,
            authored_by=author.id,
            amended_from_id=document.id,
        )

        self.repository.create(
            document=amended_document,
        )

        self.repository.save()
        self.repository.refresh(amended_document)

        return amended_document