from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.patients.models.patient import (
    BloodGroup,
    Genotype,
    MaritalStatus,
    Relationship,
    Sex,
)


class CreatePatientRequest(BaseModel):
    hospital_number: str
    first_name: str
    last_name: str
    middle_name: str | None = None

    sex: Sex
    date_of_birth: date

    phone_number: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    occupation: str | None = None

    marital_status: MaritalStatus | None = None
    religion: str | None = None

    blood_group: BloodGroup | None = None
    genotype: Genotype | None = None

    next_of_kin_name: str | None = None
    next_of_kin_relationship: Relationship | None = None
    next_of_kin_phone: str | None = None
    next_of_kin_address: str | None = None


class UpdatePatientRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None

    phone_number: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    occupation: str | None = None

    marital_status: MaritalStatus | None = None
    religion: str | None = None

    blood_group: BloodGroup | None = None
    genotype: Genotype | None = None

    next_of_kin_name: str | None = None
    next_of_kin_relationship: Relationship | None = None
    next_of_kin_phone: str | None = None
    next_of_kin_address: str | None = None


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hospital_number: str

    first_name: str
    last_name: str
    middle_name: str | None

    sex: Sex
    date_of_birth: date

    phone_number: str | None
    email: str | None
    address: str | None
    occupation: str | None

    marital_status: MaritalStatus | None
    religion: str | None

    blood_group: BloodGroup | None
    genotype: Genotype | None

    next_of_kin_name: str | None
    next_of_kin_relationship: Relationship | None
    next_of_kin_phone: str | None
    next_of_kin_address: str | None


class PatientListResponse(BaseModel):
    total: int
    items: list[PatientResponse]