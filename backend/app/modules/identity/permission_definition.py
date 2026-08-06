"""
========================================================================

LIGHTBURGH EMR

Permission Definition

========================================================================

Purpose
-------

Defines the immutable structure of a platform permission.

Permission definitions are used by the permission registry and the
permission seeder.

========================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionDefinition:
    """
    Immutable definition of a platform permission.
    """

    code: str
    name: str
    description: str