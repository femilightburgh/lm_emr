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
        Persist a newly created user account.
        """

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def save(self):
        """
        Commit pending database changes.
        """

        self.db.commit()

    def refresh(self, entity):
        """
        Reload an entity from the database.
        """

        self.db.refresh(entity)