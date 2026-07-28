"""
========================================================================

LIGHTBURGH EMR

Identity Service (Compatibility Layer)

========================================================================

Purpose
-------

This module preserves backwards compatibility for existing imports.

AuthenticationService now lives in
`authentication_service.py`.

Future services (UserService, RoleService, PermissionService)
will live in their own modules.

========================================================================
"""

from app.modules.identity.authentication_service import AuthenticationService

__all__ = [
    "AuthenticationService",
]