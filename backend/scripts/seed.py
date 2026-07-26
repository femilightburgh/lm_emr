"""
========================================================

LIGHTBURGH EMR

Database Seeder

========================================================

Usage

python -m scripts.seed

========================================================
"""
import app.models
from app.db.session import SessionLocal

from scripts.seeds.hospitals import seed_hospitals
from scripts.seeds.permissions import seed_permissions
from scripts.seeds.roles import seed_roles
from scripts.seeds.users import seed_users


def seed_database():

    print("\n==============================")
    print("LIGHTBURGH Database Seeding")
    print("==============================\n")

    db = SessionLocal()

    try:

        seed_hospitals(db)

        seed_permissions(db)

        seed_roles(db)

        seed_users(db)

        db.commit()

        print("\nDatabase successfully seeded.\n")

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_database()