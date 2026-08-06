"""
========================================================================

LIGHTBURGH EMR

Permission Bootstrap

========================================================================

Purpose
-------

Bootstraps the platform permission subsystem.

Responsibilities
----------------
- Register permission catalogues
- Synchronize permissions with the database

========================================================================
"""

from sqlalchemy.orm import Session

from app.modules.identity.core_permissions import PERMISSIONS
from app.modules.identity.permission_repository import PermissionRepository
from app.modules.identity.permission_service import PermissionService
from app.modules.identity.registry import permission_registry


def bootstrap_permissions(
    session: Session,
) -> None:
    """
    Initialize the platform permission subsystem.
    """

    _register_permission_catalogues()

    repository = PermissionRepository(session)

    service = PermissionService(repository)

    service.sync_permissions()


def _register_permission_catalogues() -> None:
    """
    Register all platform permission catalogues.
    """

    permission_registry.register(PERMISSIONS)