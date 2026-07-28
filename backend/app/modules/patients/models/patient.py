from datetime import date

from sqlalchemy import Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_entity import BaseEntity
from app.modules.patients.enums import (
    BloodGroup,
    Genotype,
    MaritalStatus,
    Relationship,
    Sex,
)


class Patient(BaseEntity):
    __tablename__ = "patients"

    # ==========================
    # Hospital Information
    # ==========================

    hospital_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    # ==========================
    # Personal Information
    # ==========================

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    middle_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    sex: Mapped[Sex] = mapped_column(
        Enum(Sex),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # ==========================
    # Contact Information
    # ==========================

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ==========================
    # Demographics
    # ==========================

    occupation: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    marital_status: Mapped[MaritalStatus | None] = mapped_column(
        Enum(MaritalStatus),
        nullable=True,
    )

    religion: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    blood_group: Mapped[BloodGroup | None] = mapped_column(
        Enum(BloodGroup),
        nullable=True,
    )

    genotype: Mapped[Genotype | None] = mapped_column(
        Enum(Genotype),
        nullable=True,
    )

    # ==========================
    # Next of Kin
    # ==========================

    next_of_kin_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    next_of_kin_relationship: Mapped[Relationship | None] = mapped_column(
        Enum(Relationship),
        nullable=True,
    )

    next_of_kin_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    next_of_kin_address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )