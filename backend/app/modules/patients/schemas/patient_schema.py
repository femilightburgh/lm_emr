from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.modules.patients.models.patient import (
    BloodGroup,
    Genotype,
    MaritalStatus,
    Relationship,
    Sex,
)


def _normalize_enum_value(value, enum_type):
    if value is None:
        return value

    if isinstance(value, enum_type):
        return value

    normalized = str(value).strip()
    if not normalized:
        return value

    for member in enum_type:
        if normalized.lower() == member.value.lower():
            return member

    return value


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

    @field_validator("sex", "marital_status", "blood_group", "genotype", "next_of_kin_relationship", mode="before")
    @classmethod
    def normalize_enum_fields(cls, value, info):
        field_name = info.field_name
        enum_map = {
            "sex": Sex,
            "marital_status": MaritalStatus,
            "blood_group": BloodGroup,
            "genotype": Genotype,
            "next_of_kin_relationship": Relationship,
        }
        enum_type = enum_map.get(field_name)
        if enum_type is None:
            return value
        return _normalize_enum_value(value, enum_type)


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