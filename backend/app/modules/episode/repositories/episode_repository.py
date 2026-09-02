"""
==============================================================================
LIGHTBURGH EMR

Episode Repository

==============================================================================

Provides persistence operations for Episodes of Care.

Business rules belong in EpisodeService.

Hospital tenancy is enforced by repository query predicates.
==============================================================================
"""

from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.modules.episode.models import (
    Episode,
    EpisodeFlowStatus,
    EpisodeStatus,
)
from app.modules.encounter.models import (
    Encounter,
    EncounterStatus,
)
from app.modules.organization.models import Department
from app.modules.patients.models import Patient
from app.modules.staff.models import (
    Staff,
    StaffEmployment,
)


class EpisodeRepository:
    """
    Repository for Episode persistence.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # =========================================================================
    # Reception Overview
    # =========================================================================

    def count_admitted_by_hospital(
        self,
        *,
        hospital_id: UUID,
    ) -> int:
        """
        Count Episodes currently on admission within a Hospital.
        """
        return int(
            self.db.scalar(
                select(
                    func.count(Episode.id),
                ).where(
                    Episode.hospital_id == hospital_id,
                    Episode.status == EpisodeStatus.ADMITTED,
                )
            )
            or 0
        )

    def count_checked_in_between(
        self,
        *,
        hospital_id: UUID,
        start_at,
        end_at,
    ) -> int:
        """
        Count Episodes checked in within a supplied time interval.
        """
        return int(
            self.db.scalar(
                select(
                    func.count(Episode.id),
                ).where(
                    Episode.hospital_id == hospital_id,
                    Episode.checked_in_at >= start_at,
                    Episode.checked_in_at < end_at,
                )
            )
            or 0
        )

    # =========================================================================
    # Create
    # =========================================================================

    def create(
        self,
        *,
        episode: Episode,
    ) -> Episode:
        """
        Add an Episode to the current transaction.
        """

        self.db.add(episode)

        return episode

    # =========================================================================
    # Retrieve
    # =========================================================================

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        episode_id: UUID,
    ) -> Episode | None:
        """
        Retrieve an Episode by ID within a Hospital.
        """

        statement = (
            select(Episode)
            .where(
                Episode.id == episode_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    # =========================================================================
    # Episode Number
    # =========================================================================

    def get_by_episode_number(
        self,
        *,
        hospital_id: UUID,
        episode_number: str,
    ) -> Episode | None:
        """
        Retrieve an Episode by hospital-scoped episode number.
        """

        statement = (
            select(Episode)
            .where(
                Episode.hospital_id == hospital_id,
                Episode.episode_number == episode_number,
            )
        )

        return self.db.scalar(statement)

    def get_latest_episode_number(
        self,
        *,
        hospital_id: UUID,
    ) -> str | None:
        """
        Retrieve the latest Episode number assigned to a Hospital.
        """

        statement = (
            select(Episode.episode_number)
            .where(
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                Episode.episode_number.desc(),
            )
            .limit(1)
        )

        return self.db.scalar(statement)

    # =========================================================================
    # Nursing Queue
    # =========================================================================

    def list_nursing_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[Episode]:
        """
        Return Episodes currently requiring nursing attention.

        Includes:

            WAITING_FOR_NURSING
            NURSING_IN_PROGRESS

        Results are ordered by check-in time so the oldest patient
        appears first.
        """

        statement = (
            select(Episode)
            .where(
                Episode.hospital_id == hospital_id,
                Episode.flow_status.in_(
                    (
                        EpisodeFlowStatus.WAITING_FOR_NURSING,
                        EpisodeFlowStatus.NURSING_IN_PROGRESS,
                    ),
                ),
            )
            .order_by(
                Episode.checked_in_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Doctor Clinic Queue
    # =========================================================================

    def list_doctor_clinic_queue(
        self,
        *,
        hospital_id: UUID,
    ) -> list[Episode]:
        """
        Return open Episodes routed to the Doctor workflow.
        """

        statement = (
            select(Episode)
            .join(
                Patient,
                Patient.id == Episode.patient_id,
            )
            .where(
                Episode.hospital_id == hospital_id,
                Episode.status == EpisodeStatus.OPEN,
                Episode.flow_status.in_(
                    (
                        EpisodeFlowStatus.ROUTED,
                        EpisodeFlowStatus.AWAITING_REVIEW,
                    ),
                ),
            )
            .order_by(
                Episode.routed_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )


    # =========================================================================
    # Nursing Inpatients
    # =========================================================================

    def list_admitted_episodes(
        self,
        *,
        hospital_id: UUID,
    ) -> list[Episode]:
        """
        Return Episodes currently on admission within a Hospital.
        """

        statement = (
            select(Episode)
            .join(
                Patient,
                Patient.id == Episode.patient_id,
            )
            .where(
                Episode.hospital_id == hospital_id,
                Episode.status == EpisodeStatus.ADMITTED,
            )
            .order_by(
                Episode.routed_at.asc().nulls_last(),
                Episode.created_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )


    # =========================================================================
    # Doctor Ward Queue
    # =========================================================================

    def list_doctor_ward_queue(
        self,
        *,
        hospital_id: UUID,
        managing_doctor_id: UUID,
    ) -> list[Episode]:
        """
        Return admitted Episodes managed by the authenticated Doctor.
        """

        statement = (
            select(Episode)
            .join(
                Patient,
                Patient.id == Episode.patient_id,
            )
            .where(
                Episode.hospital_id == hospital_id,
                Episode.status == EpisodeStatus.ADMITTED,
                Episode.managing_doctor_id == managing_doctor_id,
            )
            .order_by(
                Episode.routed_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    # =========================================================================
    # Reception Patient Flow
    # =========================================================================

    def count_flow_status_checked_in_between(
        self,
        *,
        hospital_id: UUID,
        flow_status: EpisodeFlowStatus,
        start_at,
        end_at,
    ) -> int:
        """
        Count active Episodes in a flow state that were
        checked in within a supplied time interval.
        """
        return int(
            self.db.scalar(
                select(
                    func.count(Episode.id),
                ).where(
                    Episode.hospital_id == hospital_id,
                    Episode.status == EpisodeStatus.OPEN,
                    Episode.flow_status == flow_status,
                    Episode.checked_in_at >= start_at,
                    Episode.checked_in_at < end_at,
                )
            )
            or 0
        )

    def count_flow_status_by_hospital(
        self,
        *,
        hospital_id: UUID,
        flow_status: EpisodeFlowStatus,
    ) -> int:
        """
        Count active Episodes in a specific operational flow state.
        """
        return int(
            self.db.scalar(
                select(
                    func.count(Episode.id),
                ).where(
                    Episode.hospital_id == hospital_id,
                    Episode.status == EpisodeStatus.OPEN,
                    Episode.flow_status == flow_status,
                )
            )
            or 0
        )

    def list_patient_flow(
        self,
        *,
        hospital_id: UUID,
    ) -> list[
        tuple[
            Episode,
            Patient,
            Encounter | None,
            Staff | None,
            StaffEmployment | None,
            Department | None,
        ]
    ]:
        """
        Return active Episodes with current patient-flow context.

        The active OPEN Encounter, when present, identifies the
        professional currently handling the patient.
        """

        latest_open_encounter = (
            select(
                Encounter.id.label(
                    "encounter_id",
                ),
            )
            .where(
                Encounter.episode_id == Episode.id,
                Encounter.status == EncounterStatus.OPEN,
            )
            .order_by(
                Encounter.started_at.desc(),
            )
            .limit(1)
            .correlate(Episode)
            .scalar_subquery()
        )

        statement = (
            select(
                Episode,
                Patient,
                Encounter,
                Staff,
                StaffEmployment,
                Department,
            )
            .join(
                Patient,
                Patient.id == Episode.patient_id,
            )
            .outerjoin(
                Encounter,
                Encounter.id == latest_open_encounter,
            )
            .outerjoin(
                Staff,
                Staff.id == Encounter.staff_id,
            )
            .outerjoin(
                StaffEmployment,
                and_(
                    StaffEmployment.staff_id == Staff.id,
                    StaffEmployment.employment_status == "ACTIVE",
                    StaffEmployment.date_left.is_(None),
                ),
            )
            .outerjoin(
                Department,
                Department.id == Episode.current_department_id,
            )
            .where(
                Episode.hospital_id == hospital_id,
                Patient.hospital_id == hospital_id,
                Episode.status.in_(
                    (
                        EpisodeStatus.OPEN,
                        EpisodeStatus.ADMITTED,
                    ),
                ),
            )
            .order_by(
                Episode.checked_in_at.desc().nullslast(),
                Episode.opened_at.desc(),
            )
        )

        return list(
            self.db.execute(statement).all(),
        )


    # =========================================================================
    # Patient Episodes
    # =========================================================================

    def list_by_patient(
        self,
        *,
        hospital_id: UUID,
        patient_id: UUID,
    ) -> list[Episode]:
        """
        Return all Episodes belonging to a Patient
        within the authenticated Hospital.
        """

        statement = (
            select(Episode)
            .where(
                Episode.hospital_id == hospital_id,
                Episode.patient_id == patient_id,
            )
            .order_by(
                Episode.opened_at.desc(),
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
        episode: Episode,
    ) -> None:
        """
        Refresh an Episode from the database.
        """

        self.db.refresh(episode)

    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """

        self.db.rollback()