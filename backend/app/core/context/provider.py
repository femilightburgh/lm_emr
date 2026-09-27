"""
========================================================================

LIGHTBURGH EMR

Request Context Provider

========================================================================

Purpose
-------

Constructs a RequestContext from an authenticated user.

The provider isolates the logic required to determine the effective
permissions associated with the current request.

========================================================================
"""

from datetime import UTC, datetime

from app.core.context.request_context import RequestContext
from app.modules.identity.models import UserAccount


class RequestContextProvider:
    """
    Builds RequestContext objects.
    """

    def build(
        self,
        *,
        user: UserAccount,
    ) -> RequestContext:
        """
        Construct a RequestContext for the authenticated user.
        """

        permissions: set[str] = set()

        for user_role in user.user_roles:

            if not user_role.is_active:
                continue

            if (
                user_role.expires_at is not None
                and user_role.expires_at <= datetime.now(UTC)
            ):
                continue

            role = user_role.role

            if role is None or role.hospital_id != user.hospital_id:
                continue

            for role_permission in role.role_permissions:
                permissions.add(
                    role_permission.permission.code,
                )

        return RequestContext(
            user_id=user.id,
            hospital_id=user.hospital_id,
            permissions=frozenset(permissions),
        )