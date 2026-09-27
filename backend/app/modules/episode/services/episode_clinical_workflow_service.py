"""
==============================================================================
LIGHTBURGH EMR

Episode Clinical Workflow Service
==============================================================================

Cross-module clinical workflow operations belonging to an Episode.

This service coordinates downstream clinical destinations without owning
HTTP concerns or database transactions.
==============================================================================
"""

from app.core.context import RequestContext

from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.encounter.models import EncounterStatus
from app.modules.encounter.services.encounter_service import (
    EncounterService,
)
from app.modules.episode.exceptions import (
    InvalidConsultationDispositionError,
)
from app.modules.episode.models import (
    Episode,
    EpisodeFlowStatus,
)


class EpisodeClinicalWorkflowService:
    """
    Clinical workflow operations that span multiple Episode modules.
    """

    def __init__(
        self,
        *,
        clinical_order_repository: ClinicalOrderRepository,
        encounter_service: EncounterService,
    ) -> None:
        self.clinical_order_repository = clinical_order_repository
        self.encounter_service = encounter_service

    def queue_doctor_review_if_ready(
        self,
        *,
        context: RequestContext,
        episode: Episode,
    ) -> None:
        """
        Move an Episode to AWAITING_REVIEW and create its open
        Doctor Review Encounter once all investigations are complete.

        The caller owns the surrounding database transaction.
        """

        if episode.flow_status != EpisodeFlowStatus.AWAITING_INVESTIGATIONS:
            return

        outstanding_orders = (
            self.clinical_order_repository
            .list_outstanding_investigation_orders_for_episode(
                hospital_id=context.hospital_id,
                episode_id=episode.id,
            )
        )

        if outstanding_orders:
            return

        if episode.managing_doctor_id is None:
            raise InvalidConsultationDispositionError(
                "Episode has no managing doctor assigned for Doctor Review.",
            )

        existing_encounters = (
            self.encounter_service.list_episode_encounters(
                context=context,
                episode_id=episode.id,
            )
        )

        has_open_doctor_review = any(
            encounter.title == "Doctor Review"
            and encounter.status == EncounterStatus.OPEN
            for encounter in existing_encounters
        )

        if not has_open_doctor_review:
            self.encounter_service.create_encounter(
                context=context,
                episode_id=episode.id,
                staff_id=episode.managing_doctor_id,
                title="Doctor Review",
                commit=False,
            )

        episode.flow_status = EpisodeFlowStatus.AWAITING_REVIEW
