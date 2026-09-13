"""
========================================================================

LIGHTBURGH EMR

Permission Repository

========================================================================

Purpose
-------

Database access layer for platform permissions.

Responsibilities
----------------
- Retrieve permissions
- Persist permissions
- Update permissions

Contains no business logic.

========================================================================
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import Permission
from app.modules.identity.permission_definition import PermissionDefinition
from app.modules.identity.exceptions import PermissionNotFoundError


class PermissionRepository:
    """
    Repository responsible for Permission persistence.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get_all(self) -> list[Permission]:
        """
        Retrieve all permissions.
        """

        return list(
            self.session.scalars(
                select(Permission)
            )
        )

    def get_by_code(
        self,
        code: str,
    ) -> Permission | None:
        """
        Retrieve a permission by its unique code.
        """

        return self.session.scalar(
            select(Permission).where(
                Permission.code == code
            )
        )
    
    def require_by_code(
        self,
        code: str,
    ) -> Permission:
        """
        Retrieve a permission by its unique code.

        Raises
        ------
        PermissionNotFoundError
            If the permission does not exist.
        """

        permission = self.get_by_code(code)

        if permission is None:
            raise PermissionNotFoundError()

        return permission

    def create_from_definition(
        self,
        definition: PermissionDefinition,
    ) -> Permission:
        """
        Create a Permission from a PermissionDefinition.
        """

        permission = Permission(
            code=definition.code,
            name=definition.name,
            description=definition.description,
            is_platform_permission=True,
            module=(definition.code.split(".")[0] if definition.code and "." in definition.code else definition.code),
            is_system_permission=False,
        )

        self.session.add(permission)

        return permission

    def flush(self) -> None:
        """
        Flush pending database changes.
        """

        self.session.flush()

    def commit(self) -> None:
        """
        Commit the current transaction.
        """

        self.session.commit()