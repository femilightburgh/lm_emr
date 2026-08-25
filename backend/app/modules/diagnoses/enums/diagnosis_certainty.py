from enum import StrEnum


class DiagnosisCertainty(StrEnum):
    SUSPECTED = "SUSPECTED"
    POSSIBLE = "POSSIBLE"
    CONFIRMED = "CONFIRMED"
    RULED_OUT = "RULED_OUT"
