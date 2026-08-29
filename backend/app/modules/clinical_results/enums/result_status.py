from enum import Enum


class ClinicalResultStatus(str, Enum):
    DRAFT = "DRAFT"
    FINAL = "FINAL"
