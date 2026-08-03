"""
========================================================================

LIGHTBURGH EMR

Authorization Dependencies

========================================================================

Purpose
-------

Reusable role-based authorization dependencies.

========================================================================
"""

from fastapi import Depends, HTTPException, status

from app.core.security.dependencies import get_current_user
from app.modules.identity.models import UserAccount


def require_role(role_name: str):
    """
    Require the authenticated user to possess a specific role.
    """

    def dependency(
        current_user: UserAccount = Depends(get_current_user),
    ) -> UserAccount:

        user_roles = {
            user_role.role.name
            for user_role in current_user.user_roles
            if user_role.is_active
        }

        if role_name not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return dependency