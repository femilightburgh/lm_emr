"""
========================================================================

LIGHTBURGH EMR

Request Context Dependencies

========================================================================

Purpose
-------

FastAPI dependencies for constructing the Request Context.

========================================================================
"""

from fastapi import Depends

from app.core.context.provider import RequestContextProvider
from app.core.context.request_context import RequestContext
from app.core.security.dependencies import get_current_user
from app.modules.identity.models import UserAccount


def get_request_context(
    current_user: UserAccount = Depends(get_current_user),
) -> RequestContext:
    """
    Build the RequestContext for the current request.
    """

    provider = RequestContextProvider()

    return provider.build(
        user=current_user,
    )