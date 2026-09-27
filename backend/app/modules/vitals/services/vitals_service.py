"""
==============================================================================
LIGHTBURGH EMR

Vitals Service
==============================================================================

Business logic for recording and retrieving patient vital signs.

Vitals are represented as Clinical Events:

    event_type = VITALS_RECORDED

The authenticated UserAccount is resolved to its Staff profile by the
VitalsService. The frontend therefore does not need to provide a Staff UUID.
==============================================================================
"""

from uuid import UUID

from app.core.context import RequestContext

from app.modules.events.enums import EventType
from app.modules.events.exceptions import (
    StaffHospitalMismatchError,
    StaffNotFoundError,
)
from app.modules.events.models import ClinicalEvent
from app.modules.events.services.event_service import (
    ClinicalEventService,
)

from app.modules.staff.repository import StaffRepository

from app.modules.vitals.schemas import CreateVitalsRequest


class VitalsService:
    """
    Service responsible for recording and retrieving patient vital signs.
    """

    def __init__(
        self,
        *,
        event_service: ClinicalEventService,
        staff_repository: StaffRepository,
    ) -> None:
        self.event_service = event_service
        self.staff_repository = staff_repository

    # ------------------------------------------------------------------
    # Authenticated Staff
    # ------------------------------------------------------------------

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        """
        Resolve the authenticated UserAccount to its Staff profile.
        """

        staff = (
            self.staff_repository.get_by_user_account_id(
                hospital_id=context.hospital_id,
                user_account_id=context.user_id,
            )
        )

        if staff is None:
            raise StaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise StaffHospitalMismatchError(
                "Staff member belongs to another hospital.",
            )

        return staff

    # ------------------------------------------------------------------
    # Record Vitals
    # ------------------------------------------------------------------

    def record_vitals(
        self,
        *,
        context: RequestContext,
        request: CreateVitalsRequest,
    ) -> ClinicalEvent:
        """
        Record patient vital signs as a Clinical Event.

        The authenticated user's Staff profile is used as the performer.
        """

        staff = self._get_authenticated_staff(
            context=context,
        )

        payload: dict = {}

        # --------------------------------------------------------------
        # Measurements
        # --------------------------------------------------------------

        if request.temperature is not None:
            payload["temperature"] = request.temperature

        if request.heart_rate is not None:
            payload["heart_rate"] = request.heart_rate

        if request.respiratory_rate is not None:
            payload["respiratory_rate"] = request.respiratory_rate

        if request.systolic_bp is not None:
            payload["systolic_bp"] = request.systolic_bp

        if request.diastolic_bp is not None:
            payload["diastolic_bp"] = request.diastolic_bp

        if request.spo2 is not None:
            payload["spo2"] = request.spo2

        if request.weight is not None:
            payload["weight"] = request.weight

        # --------------------------------------------------------------
        # Persist through ClinicalEventService
        # --------------------------------------------------------------

        return self.event_service.create_event(
            context=context,
            encounter_id=request.encounter_id,
            event_type=EventType.VITALS_RECORDED,
            performed_by=staff.id,
            occurred_at=request.occurred_at,
            payload=payload,
        )

    # ------------------------------------------------------------------
    # List Encounter Vitals
    # ------------------------------------------------------------------

    def list_encounter_vitals(
        self,
        *,
        context: RequestContext,
        encounter_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all VITALS_RECORDED events belonging to an Encounter.

        Hospital tenancy is enforced by ClinicalEventService.
        """

        events = self.event_service.list_encounter_events(
            context=context,
            encounter_id=encounter_id,
        )

        return [
            event
            for event in events
            if event.event_type == EventType.VITALS_RECORDED
        ]

    # ------------------------------------------------------------------
    # List Episode Vitals
    # ------------------------------------------------------------------

    def list_episode_vitals(
        self,
        *,
        context: RequestContext,
        episode_id: UUID,
    ) -> list[ClinicalEvent]:
        """
        Return all VITALS_RECORDED events belonging to an Episode
        within the authenticated Hospital.

        Observations from every Encounter in the Episode are included
        and returned in clinical occurrence order.
        """

        events = self.event_service.list_episode_events(
            context=context,
            episode_id=episode_id,
        )

        return [
            event
            for event in events
            if event.event_type == EventType.VITALS_RECORDED
        ]
