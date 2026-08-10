"""
==============================================================================
LIGHTBURGH EMR

Staff Dependencies
==============================================================================

Dependency injection for the Staff module.

These helpers construct repositories and services while keeping the router
clean and focused on HTTP concerns.
==============================================================================
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.organization.repository import HospitalRepository
from app.modules.staff.repository import StaffRepository
from app.modules.staff.service import StaffService
from app.modules.staff.employment_repository import (
    StaffEmploymentRepository,
)


def get_staff_repository(
    db: Session = Depends(get_db),
) -> StaffRepository:
    """
    Return a StaffRepository instance.
    """
    return StaffRepository(db)


def get_hospital_repository(
    db: Session = Depends(get_db),
) -> HospitalRepository:
    """
    Return a HospitalRepository instance.
    """
    return HospitalRepository(db)

def get_staff_employment_repository(
    db: Session = Depends(get_db),
) -> StaffEmploymentRepository:
    """
    Return a StaffEmploymentRepository instance.
    """
    return StaffEmploymentRepository(db)


def get_staff_service(
    repository: StaffRepository = Depends(get_staff_repository),
    hospital_repository: HospitalRepository = Depends(
        get_hospital_repository,
    ),
    employment_repository: StaffEmploymentRepository = Depends(
        get_staff_employment_repository,
    ),
) -> StaffService:
    """
    Return a StaffService instance.
    """
    return StaffService(
        repository=repository,
        hospital_repository=hospital_repository,
        employment_repository=employment_repository,
    )
