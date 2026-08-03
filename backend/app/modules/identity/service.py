"""
========================================================================

LIGHTBURGH EMR

Identity Service (Compatibility Layer)

========================================================================

Purpose
-------

This module preserves backwards compatibility for existing imports.

AuthService now lives in `auth_service.py`.

Future services (UserService, RoleService, PermissionService)
will live in their own modules.

========================================================================
"""

from app.modules.identity.auth_service import AuthService

__all__ = [
    "AuthService",
]