"""
==============================================================================
LIGHTBURGH EMR

Medication Scheduler Tests
==============================================================================
"""

from datetime import datetime, timezone

from app.modules.clinical_orders.enums import MedicationFrequency
from app.modules.clinical_orders.services.medication_scheduler import (
    generate_schedule,
)


UTC = timezone.utc


def test_tds_with_first_dose_now() -> None:
    start = datetime(
        2026,
        8,
        30,
        10,
        0,
        tzinfo=UTC,
    )

    end = datetime(
        2026,
        8,
        31,
        10,
        0,
        tzinfo=UTC,
    )

    result = generate_schedule(
        start_at=start,
        first_dose_at=start,
        frequency=MedicationFrequency.TDS,
        end_at=end,
    )

    assert result == [
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 14, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 20, 0, tzinfo=UTC),
        datetime(2026, 8, 31, 8, 0, tzinfo=UTC),
    ]


def test_bid_with_first_dose_now() -> None:
    start = datetime(
        2026,
        8,
        30,
        10,
        0,
        tzinfo=UTC,
    )

    end = datetime(
        2026,
        8,
        31,
        10,
        0,
        tzinfo=UTC,
    )

    result = generate_schedule(
        start_at=start,
        first_dose_at=start,
        frequency=MedicationFrequency.BID,
        end_at=end,
    )

    assert result == [
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 20, 0, tzinfo=UTC),
        datetime(2026, 8, 31, 8, 0, tzinfo=UTC),
    ]


def test_qid_with_first_dose_now() -> None:
    start = datetime(
        2026,
        8,
        30,
        10,
        0,
        tzinfo=UTC,
    )

    end = datetime(
        2026,
        8,
        31,
        10,
        0,
        tzinfo=UTC,
    )

    result = generate_schedule(
        start_at=start,
        first_dose_at=start,
        frequency=MedicationFrequency.QID,
        end_at=end,
    )

    assert result == [
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 12, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 18, 0, tzinfo=UTC),
        datetime(2026, 8, 31, 0, 0, tzinfo=UTC),
        datetime(2026, 8, 31, 6, 0, tzinfo=UTC),
    ]


def test_q12h_is_interval_based() -> None:
    start = datetime(
        2026,
        8,
        30,
        10,
        0,
        tzinfo=UTC,
    )

    end = datetime(
        2026,
        8,
        31,
        10,
        0,
        tzinfo=UTC,
    )

    result = generate_schedule(
        start_at=start,
        frequency=MedicationFrequency.Q12H,
        end_at=end,
    )

    assert result == [
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 22, 0, tzinfo=UTC),
    ]


def test_end_at_is_exclusive() -> None:
    start = datetime(
        2026,
        8,
        30,
        8,
        0,
        tzinfo=UTC,
    )

    end = datetime(
        2026,
        8,
        31,
        8,
        0,
        tzinfo=UTC,
    )

    result = generate_schedule(
        start_at=start,
        frequency=MedicationFrequency.Q12H,
        end_at=end,
    )

    assert result == [
        datetime(2026, 8, 30, 8, 0, tzinfo=UTC),
        datetime(2026, 8, 30, 20, 0, tzinfo=UTC),
    ]
