from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.diagnoses.models import ClinicalDiagnosis
from app.modules.encounter.models import Encounter
from app.modules.episode.models import Episode


class ClinicalDiagnosisRepository:
    """
    Persistence operations for Clinical Diagnoses.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        diagnosis: ClinicalDiagnosis,
    ) -> ClinicalDiagnosis:
        self.db.add(diagnosis)
        return diagnosis

    def get_by_id(
        self,
        *,
        hospital_id: UUID,
        diagnosis_id: UUID,
    ) -> ClinicalDiagnosis | None:
        statement = (
            select(ClinicalDiagnosis)
            .join(
                Encounter,
                ClinicalDiagnosis.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                ClinicalDiagnosis.episode_id == Episode.id,
            )
            .where(
                ClinicalDiagnosis.id == diagnosis_id,
                Episode.hospital_id == hospital_id,
            )
        )

        return self.db.scalar(statement)

    def list_by_encounter(
        self,
        *,
        hospital_id: UUID,
        encounter_id: UUID,
    ) -> list[ClinicalDiagnosis]:
        statement = (
            select(ClinicalDiagnosis)
            .join(
                Encounter,
                ClinicalDiagnosis.encounter_id == Encounter.id,
            )
            .join(
                Episode,
                ClinicalDiagnosis.episode_id == Episode.id,
            )
            .where(
                ClinicalDiagnosis.encounter_id == encounter_id,
                Episode.hospital_id == hospital_id,
            )
            .order_by(
                ClinicalDiagnosis.diagnosed_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    def save(self) -> None:
        self.db.commit()

    def refresh(
        self,
        diagnosis: ClinicalDiagnosis,
    ) -> None:
        self.db.refresh(diagnosis)
