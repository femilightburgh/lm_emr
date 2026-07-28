"""
========================================================================

LIGHTBURGH EMR

Identity Repository

========================================================================

Repository Responsibilities
---------------------------

The repository layer is responsible ONLY for database access.

It should never contain business rules.

Responsibilities include:

• Retrieving users
• Creating users
• Updating users
• Loading roles
• Loading permissions

Business decisions belong inside service.py.

========================================================================
"""

from uuid import UUID
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import UserAccount


class IdentityRepository:
    """
    Repository responsible for all database operations related
    to authentication and authorization.

    Services should communicate with the database only through
    this repository.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(
        self,
        hospital_id: UUID,
        email: str,
    ) -> UserAccount | None:
        """
        Retrieve a user using hospital and email.

        Because LIGHTBURGH is multi-tenant, email addresses
        are only unique inside a hospital.
        """

        statement = (
            select(UserAccount)
            .where(
                UserAccount.hospital_id == hospital_id,
                UserAccount.email == email,
            )
        )

        return self.db.scalar(statement)

    def create_user(
        self,
        user: UserAccount,
    ) -> UserAccount:
        """
        Add a newly created user to the current database session.

        This method intentionally does NOT commit the transaction.
        The service layer is responsible for deciding when the
        transaction should be committed.

        Returns
        -------
        UserAccount
            The newly added user entity.
        """

        self.db.add(user)
        return user

    def save(self) -> None:
        """
        Commit all pending database changes.
        """

        self.db.commit()

    def refresh(
        self,
        entity: Any,
    ) -> None:
        """
        Reload an entity from the database.
        """

        self.db.refresh(entity)

    def rollback(self) -> None:
        """
        Roll back the current transaction.

        Services should call this when a transaction fails.
        """

        self.db.rollback()