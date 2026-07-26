"""
========================================================================

LIGHTBURGH EMR

Organization Enumerations

========================================================================

This module contains enumerations used throughout the Organization
module.

The goal is to keep organizational metadata strongly typed while
remaining flexible enough to support hospitals from different
countries.

Design Principles
-----------------

A hospital is described using several independent characteristics.

Examples

Hospital Ownership
------------------
- Public
- Private
- Faith-Based
- Military

Hospital Type
-------------
- General Hospital
- Specialist Hospital
- Teaching Hospital

Keeping these concepts separate allows combinations such as:

• Private Specialist Hospital
• Public General Hospital
• Faith-Based Teaching Hospital
• Military General Hospital

========================================================================
"""

from enum import Enum


# ----------------------------------------------------------------------
# Hospital Ownership
# ----------------------------------------------------------------------

class HospitalOwnership(str, Enum):
    """
    Identifies who owns or operates the hospital.
    """

    PUBLIC = "Public"
    PRIVATE = "Private"
    FAITH_BASED = "Faith-Based"
    MILITARY = "Military"
    UNIVERSITY = "University"
    NGO = "Non-Governmental"


# ----------------------------------------------------------------------
# Hospital Type
# ----------------------------------------------------------------------

class HospitalType(str, Enum):
    """
    Describes the level or category of healthcare facility.
    """

    PRIMARY = "Primary Health Centre"
    GENERAL = "General Hospital"
    SPECIALIST = "Specialist Hospital"
    TEACHING = "Teaching Hospital"
    DIAGNOSTIC = "Diagnostic Centre"


# ----------------------------------------------------------------------
# Department Categories
# ----------------------------------------------------------------------

class DepartmentCategory(str, Enum):
    """
    High-level classification of hospital departments.
    """

    CLINICAL = "Clinical"
    DIAGNOSTIC = "Diagnostic"
    ADMINISTRATIVE = "Administrative"
    SUPPORT = "Support"


# ----------------------------------------------------------------------
# Ward Types
# ----------------------------------------------------------------------

class WardType(str, Enum):
    """
    Categories of inpatient wards.
    """

    MEDICAL = "Medical"
    SURGICAL = "Surgical"
    PAEDIATRIC = "Paediatric"
    ICU = "ICU"
    NICU = "NICU"
    MATERNITY = "Maternity"
    ISOLATION = "Isolation"
    EMERGENCY = "Emergency"


# ----------------------------------------------------------------------
# Theatre Types
# ----------------------------------------------------------------------

class TheatreType(str, Enum):
    """
    Categories of operating theatres.
    """

    MAJOR = "Major"
    MINOR = "Minor"
    ENDOSCOPY = "Endoscopy"
    LABOUR = "Labour Ward Theatre"
    CARDIAC = "Cardiac"
    ORTHOPAEDIC = "Orthopaedic"