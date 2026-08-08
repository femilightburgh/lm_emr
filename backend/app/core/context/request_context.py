"""
========================================================================

LIGHTBURGH EMR

Request Context

========================================================================

Purpose
-------

Defines the immutable context associated with the current request.

The Request Context provides business services with the minimum
information required to execute within the scope of the current user
and hospital.

Responsibilities
----------------
- Identify the authenticated user
- Identify the active hospital
- Expose the user's effective permissions

========================================================================
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RequestContext:
    """
    Immutable context for the current request.
    """

    user_id: UUID
    hospital_id: UUID
    permissions: frozenset[str]