from enum import Enum


class LaboratoryAnalyteDataType(str, Enum):
    NUMERIC = "NUMERIC"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    CODED = "CODED"
