"""
LIGHTBURGH EMR

Department Dependencies

Dependency injection for the Department module.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.organization.department_repository import (
    DepartmentRepository,
)
from app.modules.organization.department_service import DepartmentService
from app.modules.organization.repository import HospitalRepository


def get_department_repository(
    db: Session = Depends(get_db),
) -> DepartmentRepository:
    """
    Return a DepartmentRepository instance.
    """
    return DepartmentRepository(db)


def get_hospital_repository(
    db: Session = Depends(get_db),
) -> HospitalRepository:
    """
    Return a HospitalRepository instance.
    """
    return HospitalRepository(db)


def get_department_service(
    repository: DepartmentRepository = Depends(
        get_department_repository,
    ),
    hospital_repository: HospitalRepository = Depends(
        get_hospital_repository,
    ),
) -> DepartmentService:
    """
    Return a DepartmentService instance.
    """
    return DepartmentService(
        repository=repository,
        hospital_repository=hospital_repository,
    )