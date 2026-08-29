"""
==============================================================================
LIGHTBURGH EMR

Laboratory Test Repository
==============================================================================
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.laboratory.models import (
    LaboratoryTest,
    LaboratoryTestAnalyte,
)


class LaboratoryTestRepository:
    """
    Persistence operations for Laboratory Test catalogue entries.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def list_active(
        self,
        *,
        hospital_id,
    ) -> list[LaboratoryTest]:
        statement = (
            select(LaboratoryTest)
            .options(
                selectinload(LaboratoryTest.analytes),
            )
            .where(
                LaboratoryTest.hospital_id == hospital_id,
                LaboratoryTest.active.is_(True),
            )
            .order_by(
                LaboratoryTest.name.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    def get_by_code(
        self,
        *,
        hospital_id,
        code: str,
    ) -> LaboratoryTest | None:
        statement = (
            select(LaboratoryTest)
            .options(
                selectinload(LaboratoryTest.analytes),
            )
            .where(
                LaboratoryTest.hospital_id == hospital_id,
                LaboratoryTest.code == code,
            )
        )

        return self.db.scalar(statement)

    def get_analyte(
        self,
        *,
        hospital_id,
        test_code: str,
        analyte_id,
    ) -> LaboratoryTestAnalyte | None:
        statement = (
            select(LaboratoryTestAnalyte)
            .join(
                LaboratoryTest,
                LaboratoryTestAnalyte.laboratory_test_id
                == LaboratoryTest.id,
            )
            .where(
                LaboratoryTest.hospital_id == hospital_id,
                LaboratoryTest.code == test_code,
                LaboratoryTestAnalyte.id == analyte_id,
            )
        )

        return self.db.scalar(statement)

    def save(self) -> None:
        self.db.commit()

    def create(
        self,
        *,
        laboratory_test: LaboratoryTest,
    ) -> LaboratoryTest:
        self.db.add(laboratory_test)
        return laboratory_test


    def create_analyte(
        self,
        *,
        analyte: LaboratoryTestAnalyte,
    ) -> LaboratoryTestAnalyte:
        self.db.add(analyte)
        return analyte
