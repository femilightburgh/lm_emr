"""
==============================================================================
LIGHTBURGH EMR

Medication Nursing Summary Tests
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from app.modules.clinical_orders.enums import (
    MedicationAdministrationStatus,
    MedicationDoseStatus,
)
from app.modules.clinical_orders.services.medication_nursing_summary_service import (
    MedicationNursingSummaryService,
)


NOW = datetime(
    2026,
    9,
    1,
    9,
    0,
    tzinfo=UTC,
)


def make_dose(
    *,
    scheduled_at: datetime,
    status=MedicationDoseStatus.PENDING,
    administration=None,
):
    return SimpleNamespace(
        id=uuid4(),
        treatment_id=None,
        scheduled_at=scheduled_at,
        status=status,
        administration=administration,
    )


def make_administration(
    status: MedicationAdministrationStatus,
    *,
    administered_at: datetime | None = None,
    dose_given: str | None = None,
    reason: str | None = None,
    notes: str | None = None,
):
    return SimpleNamespace(
        id=uuid4(),
        status=status,
        administered_at=(
            administered_at
            if administered_at is not None
            else NOW
        ),
        dose_given=dose_given,
        reason=reason,
        notes=notes,
    )


def make_treatment(
    *,
    medicine_name: str,
    frequency: str = "TDS",
    doses,
):
    treatment_id = uuid4()
    prescription_id = uuid4()

    prescription = SimpleNamespace(
        id=prescription_id,
        medicine_name=medicine_name,
        strength="500 mg",
        dose="500",
        dose_unit="mg",
        route="PO",
        frequency=frequency,
        directions=None,
    )

    treatment = SimpleNamespace(
        id=treatment_id,
        prescription_id=prescription_id,
        prescription=prescription,
        doses=doses,
    )

    for dose in doses:
        dose.treatment_id = treatment_id
        dose.treatment = treatment

    return treatment


class FakeEpisodeRepository:
    def __init__(self):
        self.episode = SimpleNamespace(
            id=uuid4(),
            status="ADMITTED",
        )

    def get_by_id(
        self,
        *,
        hospital_id,
        episode_id,
    ):
        return self.episode


class FakeTreatmentRepository:
    def __init__(
        self,
        treatments,
    ):
        self.treatments = treatments

    def list_active_by_episode(
        self,
        *,
        episode_id,
    ):
        return self.treatments


def build_service(treatments):
    return MedicationNursingSummaryService(
        treatment_repository=FakeTreatmentRepository(
            treatments,
        ),
        episode_repository=FakeEpisodeRepository(),
    )


def build_context():
    return SimpleNamespace(
        hospital_id=uuid4(),
    )


def test_multiple_medications_share_one_round():
    ampiclox = make_treatment(
        medicine_name="Ampiclox",
        doses=[
            make_dose(
                scheduled_at=NOW,
            ),
            make_dose(
                scheduled_at=NOW + timedelta(hours=6),
            ),
        ],
    )

    cefotaxime = make_treatment(
        medicine_name="Cefotaxime",
        doses=[
            make_dose(
                scheduled_at=NOW + timedelta(minutes=10),
            ),
            make_dose(
                scheduled_at=NOW + timedelta(hours=6),
            ),
        ],
    )

    service = build_service(
        [
            ampiclox,
            cefotaxime,
        ],
    )

    summaries, round_groups = (
        service.build_episode_summary(
            context=build_context(),
            episode_id=uuid4(),
            now=NOW,
        )
    )

    assert len(summaries) == 2

    current_round = round_groups["current_round"]

    assert current_round is not None
    assert len(current_round["doses"]) == 2

    medicines = {
        dose["medicine_name"]
        for dose in current_round["doses"]
    }

    assert medicines == {
        "Ampiclox",
        "Cefotaxime",
    }


def test_upcoming_rounds_are_grouped():
    ampiclox = make_treatment(
        medicine_name="Ampiclox",
        doses=[
            make_dose(
                scheduled_at=NOW + timedelta(hours=5),
            ),
            make_dose(
                scheduled_at=NOW + timedelta(hours=11),
            ),
        ],
    )

    cefotaxime = make_treatment(
        medicine_name="Cefotaxime",
        doses=[
            make_dose(
                scheduled_at=NOW + timedelta(hours=5, minutes=10),
            ),
            make_dose(
                scheduled_at=NOW + timedelta(hours=11, minutes=10),
            ),
        ],
    )

    service = build_service(
        [
            ampiclox,
            cefotaxime,
        ],
    )

    _, round_groups = service.build_episode_summary(
        context=build_context(),
        episode_id=uuid4(),
        now=NOW,
    )

    upcoming_rounds = round_groups["upcoming_rounds"]

    assert len(upcoming_rounds) == 2

    assert upcoming_rounds[0]["scheduled_at"] == (
        NOW + timedelta(hours=5)
    )

    assert len(upcoming_rounds[0]["doses"]) == 2

    assert upcoming_rounds[1]["scheduled_at"] == (
        NOW + timedelta(hours=11)
    )

    assert len(upcoming_rounds[1]["doses"]) == 2


def test_previous_round_contains_resolved_outcomes():
    previous_time = NOW - timedelta(hours=4)

    ampiclox = make_treatment(
        medicine_name="Ampiclox",
        doses=[
            make_dose(
                scheduled_at=previous_time,
                administration=make_administration(
                    MedicationAdministrationStatus.GIVEN,
                    administered_at=(
                        previous_time
                        + timedelta(minutes=5)
                    ),
                ),
            ),
        ],
    )

    cefotaxime = make_treatment(
        medicine_name="Cefotaxime",
        doses=[
            make_dose(
                scheduled_at=(
                    previous_time
                    + timedelta(minutes=10)
                ),
                administration=make_administration(
                    MedicationAdministrationStatus.HELD,
                    administered_at=(
                        previous_time
                        + timedelta(minutes=8)
                    ),
                    reason="Blood pressure below parameter.",
                ),
            ),
        ],
    )

    service = build_service(
        [
            ampiclox,
            cefotaxime,
        ],
    )

    _, round_groups = service.build_episode_summary(
        context=build_context(),
        episode_id=uuid4(),
        now=NOW,
    )

    previous_round = round_groups["previous_round"]

    assert previous_round is not None
    assert len(previous_round["doses"]) == 2

    states = {
        dose["administration_status"]
        for dose in previous_round["doses"]
    }

    assert states == {
        "GIVEN",
        "HELD",
    }



def test_future_dose_preserves_scheduled_state_with_old_administration():
    future_time = NOW + timedelta(hours=11)

    dose = make_dose(
        scheduled_at=future_time,
        administration=make_administration(
            MedicationAdministrationStatus.HELD,
            administered_at=NOW - timedelta(hours=1),
            reason="Historical test administration.",
        ),
    )

    treatment = make_treatment(
        medicine_name="Ampiclox",
        doses=[dose],
    )

    service = build_service(
        [treatment],
    )

    _, round_groups = service.build_episode_summary(
        context=build_context(),
        episode_id=uuid4(),
        now=NOW,
    )

    upcoming_rounds = round_groups["upcoming_rounds"]

    assert len(upcoming_rounds) == 1

    medication = upcoming_rounds[0]["doses"][0]

    assert medication["scheduled_state"] == "UPCOMING"
    assert medication["administration_status"] == "HELD"
    assert medication["administration_at"] == (
        NOW - timedelta(hours=1)
    )
    assert medication["reason"] == (
        "Historical test administration."
    )


def test_resolved_dose_is_not_actionable_current_round():
    resolved_time = NOW - timedelta(
        minutes=30,
    )

    treatment = make_treatment(
        medicine_name="Ampiclox",
        doses=[
            make_dose(
                scheduled_at=resolved_time,
                administration=make_administration(
                    MedicationAdministrationStatus.GIVEN,
                    administered_at=resolved_time,
                ),
            ),
            make_dose(
                scheduled_at=NOW + timedelta(hours=2),
            ),
        ],
    )

    service = build_service(
        [treatment],
    )

    _, round_groups = service.build_episode_summary(
        context=build_context(),
        episode_id=uuid4(),
        now=NOW,
    )

    assert round_groups["current_round"] is None

    assert len(
        round_groups["upcoming_rounds"]
    ) == 1

def test_counts_and_remaining():
    doses = [
        make_dose(
            scheduled_at=NOW - timedelta(hours=5),
            administration=make_administration(
                MedicationAdministrationStatus.GIVEN,
            ),
        ),
        make_dose(
            scheduled_at=NOW - timedelta(hours=4),
            administration=make_administration(
                MedicationAdministrationStatus.GIVEN,
            ),
        ),
        make_dose(
            scheduled_at=NOW - timedelta(hours=3),
            administration=make_administration(
                MedicationAdministrationStatus.HELD,
            ),
        ),
        make_dose(
            scheduled_at=NOW - timedelta(hours=2),
            administration=make_administration(
                MedicationAdministrationStatus.MISSED,
            ),
        ),
        make_dose(
            scheduled_at=NOW - timedelta(hours=1),
            administration=make_administration(
                MedicationAdministrationStatus.REFUSED,
            ),
        ),
        make_dose(
            scheduled_at=NOW + timedelta(hours=1),
        ),
        make_dose(
            scheduled_at=NOW + timedelta(hours=2),
        ),
    ]

    treatment = make_treatment(
        medicine_name="Ampiclox",
        doses=doses,
    )

    service = build_service(
        [treatment],
    )

    summaries, _ = service.build_episode_summary(
        context=build_context(),
        episode_id=uuid4(),
        now=NOW,
    )

    summary = summaries[0]

    assert summary["total_scheduled"] == 7
    assert summary["given_count"] == 2
    assert summary["held_count"] == 1
    assert summary["missed_count"] == 1
    assert summary["refused_count"] == 1
    assert summary["remaining_count"] == 2

    assert summary["next_dose_at"] == (
        NOW + timedelta(hours=1)
    )

    assert summary["next_dose_state"] == "UPCOMING"
