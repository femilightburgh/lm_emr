"""
==============================================================================
LIGHTBURGH EMR

Episode Test Helpers

==============================================================================

Shared test utilities for constructing Episode-domain services.
==============================================================================
"""

from sqlalchemy.orm import Session

from app.modules.encounter.repositories.encounter_repository import (
    EncounterRepository,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_number_generator import (
    EpisodeNumberGenerator,
)
from app.modules.episode.services.episode_service import (
    EpisodeService,
)
from app.modules.events.repositories import (
    ClinicalEventRepository,
)
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.staff.repository import (
    StaffRepository,
)


def build_episode_service(
    db: Session,
) -> EpisodeService:
    """
    Build an EpisodeService with its complete production dependency graph.
    """

    repository = EpisodeRepository(
        db,
    )

    return EpisodeService(
        repository=repository,
        patient_repository=PatientRepository(
            db,
        ),
        number_generator=EpisodeNumberGenerator(
            repository=repository,
        ),
        encounter_repository=EncounterRepository(
            db,
        ),
        event_service=ClinicalEventService(
            repository=ClinicalEventRepository(
                db,
            ),
        ),
        staff_repository=StaffRepository(
            session=db,
        ),
    )