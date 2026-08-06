"""
========================================================================

LIGHTBURGH EMR

Application Bootstrap

========================================================================

Purpose
-------

Coordinates application startup.

Each bootstrap component is responsible for initializing a specific
part of the platform.

========================================================================
"""

from app.bootstrap.permissions import bootstrap_permissions
from app.db.session import SessionLocal


def bootstrap_application() -> None:
    """
    Initialize the LIGHTBURGH platform.
    """

    with SessionLocal() as session:

        bootstrap_permissions(session)

        session.commit()