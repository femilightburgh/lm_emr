"""
========================================================================

LIGHTBURGH EMR

Authorization Dependencies

========================================================================

Purpose
-------

Reusable FastAPI authorization dependencies.

Business rules belong to AuthorizationService.

========================================================================
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security.authorization_repository import (
    AuthorizationRepository,
)
from app.core.security.authorization_service import (
    AuthorizationService,
)
from app.core.security.dependencies import get_current_user
from app.db.session import get_db
from app.modules.identity.exceptions import PermissionDeniedError
from app.modules.identity.models import UserAccount


def get_authorization_service(
    db: Session = Depends(get_db),
) -> AuthorizationService:
    """
    Build the runtime authorization service.
    """

    repository = AuthorizationRepository(db)

    return AuthorizationService(
        repository=repository,
    )


def require_role(
    role_name: str,
):
    """
    Require the authenticated user to possess a specific role.
    """

    def dependency(
        current_user: UserAccount = Depends(get_current_user),
        service: AuthorizationService = Depends(
            get_authorization_service,
        ),
    ) -> UserAccount:

        if not service.has_role(
            user_id=current_user.id,
            role_name=role_name,
        ):
            raise PermissionDeniedError()

        return current_user

    return dependency


def require_permission(
    permission_code: str,
):
    """
    Require the authenticated user to possess a specific permission.
    """

    def dependency(
        current_user: UserAccount = Depends(get_current_user),
        service: AuthorizationService = Depends(
            get_authorization_service,
        ),
    ) -> UserAccount:

        if not service.has_permission(
            user_id=current_user.id,
            permission_code=permission_code,
        ):
            raise PermissionDeniedError()

        return current_user

    return dependency