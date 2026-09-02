"""
==============================================================================
LIGHTBURGH EMR

Reception Service
==============================================================================

Purpose
-------
Provides business logic for the Reception workspace.

Persistence remains in the PatientRepository and EpisodeRepository.
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from app.modules.episode.models import EpisodeFlowStatus
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.organization.repository import (
    HospitalRepository,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.reception.schemas import (
    ReceptionOverviewResponse,
    ReceptionPatientFlowItem,
    ReceptionPatientFlowResponse,
)


class ReceptionService:
    """
    Business logic for the Reception workspace.
    """

    def __init__(
        self,
        *,
        patient_repository: PatientRepository,
        episode_repository: EpisodeRepository,
        hospital_repository: HospitalRepository,
    ) -> None:
        self.patient_repository = patient_repository
        self.episode_repository = episode_repository
        self.hospital_repository = hospital_repository

    def list_patient_flow(
        self,
        *,
        hospital_id: UUID,
    ) -> ReceptionPatientFlowResponse:
        """
        Return active patient-flow records for Reception.
        """

        records = self.episode_repository.list_patient_flow(
            hospital_id=hospital_id,
        )

        items = []

        for (
            episode,
            patient,
            encounter,
            staff,
            employment,
            department,
        ) in records:
            professional_name = None

            if staff is not None:
                professional_name = (
                    f"Dr. {staff.first_name} "
                    f"{staff.last_name}"
                    if employment is not None
                    and employment.profession.value == "DOCTOR"
                    else (
                        f"{staff.first_name} "
                        f"{staff.last_name}"
                    )
                )

            professional_role = (
                employment.profession.value
                if employment is not None
                else None
            )

            department_name = (
                department.name
                if department is not None
                else None
            )

            items.append(
                ReceptionPatientFlowItem(
                    id=episode.id,
                    patient_id=episode.patient_id,
                    patient_name=(
                        f"{patient.last_name}, "
                        f"{patient.first_name}"
                    ),
                    hospital_number=patient.hospital_number,
                    episode_number=episode.episode_number,
                    title=episode.title,
                    status=episode.status,
                    flow_status=episode.flow_status,
                    professional_name=professional_name,
                    professional_role=professional_role,
                    department_name=department_name,
                    checked_in_at=episode.checked_in_at,
                    opened_at=episode.opened_at,
                )
            )

        return ReceptionPatientFlowResponse(
            items=items,
        )


    def get_overview(
        self,
        *,
        hospital_id: UUID,
    ) -> ReceptionOverviewResponse:
        """
        Return hospital-wide Reception overview statistics.
        """

        hospital = (
            self.hospital_repository.get_hospital_by_id(
                hospital_id,
            )
        )

        if hospital is None:
            raise ValueError(
                "Hospital not found.",
            )

        try:
            hospital_timezone = ZoneInfo(
                hospital.timezone,
            )
        except Exception as exc:
            raise ValueError(
                f"Invalid hospital timezone: {hospital.timezone}",
            ) from exc

        now_local = datetime.now(
            hospital_timezone,
        )

        start_of_today_local = datetime(
            now_local.year,
            now_local.month,
            now_local.day,
            tzinfo=hospital_timezone,
        )

        start_of_tomorrow_local = (
            start_of_today_local +
            timedelta(days=1)
        )

        start_of_today_utc = (
            start_of_today_local.astimezone(UTC)
        )

        start_of_tomorrow_utc = (
            start_of_tomorrow_local.astimezone(UTC)
        )

        return ReceptionOverviewResponse(
            total_patients=(
                self.patient_repository.count_by_hospital(
                    hospital_id,
                )
            ),
            currently_admitted=(
                self.episode_repository.count_admitted_by_hospital(
                    hospital_id=hospital_id,
                )
            ),
            checked_in_today=(
                self.episode_repository.count_checked_in_between(
                    hospital_id=hospital_id,
                    start_at=start_of_today_utc,
                    end_at=start_of_tomorrow_utc,
                )
            ),
            waiting_for_nursing=(
                self.episode_repository.count_flow_status_checked_in_between(
                    hospital_id=hospital_id,
                    flow_status=(
                        EpisodeFlowStatus.WAITING_FOR_NURSING
                    ),
                    start_at=start_of_today_utc,
                    end_at=start_of_tomorrow_utc,
                )
            ),
            nursing_in_progress=(
                self.episode_repository.count_flow_status_checked_in_between(
                    hospital_id=hospital_id,
                    flow_status=(
                        EpisodeFlowStatus.NURSING_IN_PROGRESS
                    ),
                    start_at=start_of_today_utc,
                    end_at=start_of_tomorrow_utc,
                )
            ),
            routed=(
                self.episode_repository.count_flow_status_checked_in_between(
                    hospital_id=hospital_id,
                    flow_status=(
                        EpisodeFlowStatus.ROUTED
                    ),
                    start_at=start_of_today_utc,
                    end_at=start_of_tomorrow_utc,
                )
            ),
            awaiting_investigations=(
                self.episode_repository.count_flow_status_checked_in_between(
                    hospital_id=hospital_id,
                    flow_status=(
                        EpisodeFlowStatus.AWAITING_INVESTIGATIONS
                    ),
                    start_at=start_of_today_utc,
                    end_at=start_of_tomorrow_utc,
                )
            ),
            awaiting_review=(
                self.episode_repository.count_flow_status_checked_in_between(
                    hospital_id=hospital_id,
                    flow_status=(
                        EpisodeFlowStatus.AWAITING_REVIEW
                    ),
                    start_at=start_of_today_utc,
                    end_at=start_of_tomorrow_utc,
                )
            ),
        )

