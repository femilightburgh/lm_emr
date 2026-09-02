"""
==============================================================================
LIGHTBURGH EMR

Organization Service

==============================================================================

Business logic for Organization management.

==============================================================================
"""

from sqlalchemy.orm import Session

from app.common.exceptions import DuplicateResourceException
from app.modules.identity.role_seeder import seed_default_roles
from app.bootstrap.diagnostics import bootstrap_diagnostic_investigations
from app.modules.organization.models import Hospital
from app.modules.organization.repository import HospitalRepository
from app.modules.organization.schemas import HospitalCreate


class HospitalService:
    """
    Handles hospital-related business logic.
    """

    def __init__(self, db: Session):
        self.repository = HospitalRepository(db)

    def create_hospital(
        self,
        request: HospitalCreate,
    ) -> Hospital:
        """
        Create a new hospital.
        """

        existing = self.repository.get_hospital_by_code(
            request.code
        )

        if existing:
            raise DuplicateResourceException(
                f"A hospital with code '{request.code}' already exists."
            )

        hospital = Hospital(
            name=request.name,
            code=request.code,
            hospital_type=request.hospital_type,
            ownership=request.ownership,
            email=request.email,
            phone=request.phone,
            website=request.website,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            timezone=request.timezone,
            logo_url=request.logo_url,
            license_number=request.license_number,
        )

        try:
            self.repository.create_hospital(hospital)

            self.repository.flush()

            seed_default_roles(
                db=self.repository.db,
                hospital_id=hospital.id,
            )

            bootstrap_diagnostic_investigations(
                session=self.repository.db,
                hospital_id=hospital.id,
            )

            self.repository.save()

            self.repository.refresh(hospital)

            return hospital

        except Exception:
            self.repository.rollback()
            raise