"""
==============================================================================
LIGHTBURGH EMR

Medication Round Service Tests
==============================================================================
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.modules.clinical_orders.services.medication_round_service import (
    MedicationRoundService,
)


NOW = datetime(
    2026,
    9,
    1,
    9,
    0,
    tzinfo=UTC,
)


def dose(minutes_from_now: int):
    return SimpleNamespace(
        scheduled_at=NOW + timedelta(
            minutes=minutes_from_now,
        )
    )


def test_doses_within_thirty_minutes_share_a_round():
    doses = [
        dose(-60),
        dose(-45),
        dose(-31),
        dose(60),
    ]

    rounds = MedicationRoundService.group_doses(
        doses=doses,
    )

    assert len(rounds) == 2
    assert len(rounds[0]) == 3
    assert len(rounds[1]) == 1


def test_more_than_thirty_minutes_starts_new_round():
    doses = [
        dose(0),
        dose(30),
        dose(61),
    ]

    rounds = MedicationRoundService.group_doses(
        doses=doses,
    )

    assert len(rounds) == 2
    assert len(rounds[0]) == 2
    assert len(rounds[1]) == 1


def test_previous_round_is_selected():
    doses = [
        dose(-780),
        dose(-420),
        dose(-60),
        dose(-45),
        dose(300),
    ]

    previous = MedicationRoundService.find_previous_round(
        doses=doses,
        now=NOW,
    )

    assert previous is not None
    assert [item.scheduled_at for item in previous] == [
        NOW - timedelta(minutes=60),
        NOW - timedelta(minutes=45),
    ]


def test_current_or_next_round_is_selected():
    doses = [
        dose(-60),
        dose(-45),
        dose(300),
        dose(315),
    ]

    current = MedicationRoundService.find_current_or_next_round(
        doses=doses,
        now=NOW,
    )

    assert current is not None
    assert [item.scheduled_at for item in current] == [
        NOW + timedelta(minutes=300),
        NOW + timedelta(minutes=315),
    ]
