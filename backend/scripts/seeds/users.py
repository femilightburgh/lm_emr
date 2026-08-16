"""
========================================================

LIGHTBURGH EMR

User Seeder

========================================================
"""

from sqlalchemy.orm import Session

from app.modules.identity.repository import IdentityRepository
from app.modules.identity.user_service import UserService


DEMO_USERS = [
    {
        "hospital_code": "LIGHT001",
        "email": "receptionist@lightburgh.com",
        "password": "password123",
        "role_name": "Receptionist",
    },
]


def seed_users(db: Session) -> None:
    """
    Seed default development/demo users.

    This seeder is idempotent.
    """

    print("✓ Seeding users...")

    repository = IdentityRepository(db)
    service = UserService(repository)

    for user_data in DEMO_USERS:
        existing_user = repository.get_user_by_email(
            hospital_id=(
                repository
                .get_hospital_by_code(
                    user_data["hospital_code"],
                )
                .id
            ),
            email=user_data["email"],
        )

        if existing_user is not None:
            print(
                f"  • User already exists: "
                f"{user_data['email']}"
            )
            continue

        service.create_user(
            hospital_code=user_data["hospital_code"],
            email=user_data["email"],
            password=user_data["password"],
            role_name=user_data["role_name"],
        )

        print(
            f"  • Created {user_data['role_name']}: "
            f"{user_data['email']}"
        )