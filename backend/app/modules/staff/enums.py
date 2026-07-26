"""
========================================================================

LIGHTBURGH EMR

Staff Enumerations

========================================================================

This module defines enumerations used by the Staff module.

Separating enumerations into their own module improves readability,
maintains consistency across the application, and prevents the use
of arbitrary string values in the database.

========================================================================
"""

from enum import Enum


# ----------------------------------------------------------------------
# Gender
# ----------------------------------------------------------------------

class Gender(str, Enum):
    """
    Biological sex recorded for the staff member.

    This field is stored for clinical, regulatory, and employment
    purposes.
    """

    MALE = "Male"
    FEMALE = "Female"


# ----------------------------------------------------------------------
# Employment Status
# ----------------------------------------------------------------------

class EmploymentStatus(str, Enum):
    """
    Indicates the staff member's current employment status.
    """

    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    SUSPENDED = "Suspended"
    RESIGNED = "Resigned"
    RETIRED = "Retired"
    TERMINATED = "Terminated"


# ----------------------------------------------------------------------
# Employment Type
# ----------------------------------------------------------------------

class EmploymentType(str, Enum):
    """
    Describes the nature of the staff member's employment.
    """

    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    LOCUM = "Locum"
    INTERN = "Intern"
    RESIDENT = "Resident"
    VISITING = "Visiting"


# ----------------------------------------------------------------------
# Profession
# ----------------------------------------------------------------------

class Profession(str, Enum):
    """
    Represents the healthcare or administrative profession
    of a staff member.
    """

    DOCTOR = "Doctor"
    NURSE = "Nurse"
    PHARMACIST = "Pharmacist"
    LABORATORY_SCIENTIST = "Laboratory Scientist"
    RADIOGRAPHER = "Radiographer"
    PHYSIOTHERAPIST = "Physiotherapist"
    DIETITIAN = "Dietitian"
    DENTIST = "Dentist"

    RECEPTIONIST = "Receptionist"
    RECORDS_OFFICER = "Records Officer"
    ACCOUNTANT = "Accountant"
    ADMINISTRATOR = "Administrator"
    IT_SUPPORT = "IT Support"

    OTHER = "Other"