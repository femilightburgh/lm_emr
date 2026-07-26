from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_entity import BaseEntity


class Patient(BaseEntity):
    __tablename__ = "patients"

    hospital_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    middle_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    sex: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )
