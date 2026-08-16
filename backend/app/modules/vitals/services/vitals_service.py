"""
==============================================================================
LIGHTBURGH EMR

Vitals Service
==============================================================================

Business logic for recording patient vital signs.

Vitals are represented as Clinical Events:

    event_type = VITALS_RECORDED

The VitalsService is intentionally thin. It is responsible for:

    • validating the Vitals-specific request
    • constructing the structured clinical payload
    • delegating persistence and tenancy enforcement to ClinicalEventService

Persistence remains owned by the Events module.
==============================================================================
"""

from app.core.context import RequestContext
from app.modules.events.enums import EventType
from app.modules.events.models import ClinicalEvent
from app.modules.events.services.event_service import ClinicalEventService
from app.modules.vitals.schemas import CreateVitalsRequest


class VitalsService:
    """
    Service responsible for recording patient vital signs.
    """

    def __init__(
        self,
        *,
        event_service: ClinicalEventService,
    ) -> None:
        self.event_service = event_service

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

        The event is persisted with:

            event_type = VITALS_RECORDED

        Only measurements actually supplied by the caller are included
        in the payload.
        """

        payload = {}

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
            performed_by=request.performed_by,
            occurred_at=request.occurred_at,
            payload=payload,
        )