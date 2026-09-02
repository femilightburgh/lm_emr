"""
==============================================================================
LIGHTBURGH EMR

Medication Scheduler
==============================================================================
"""

from datetime import datetime, time, timedelta

from app.modules.clinical_orders.enums import (
    MedicationFrequency,
)


FREQUENCY_INTERVALS = {
    MedicationFrequency.Q2H: timedelta(hours=2),
    MedicationFrequency.Q4H: timedelta(hours=4),
    MedicationFrequency.Q6H: timedelta(hours=6),
    MedicationFrequency.Q8H: timedelta(hours=8),
    MedicationFrequency.Q12H: timedelta(hours=12),
    MedicationFrequency.Q24H: timedelta(hours=24),
}


DEFAULT_DAILY_TIMES = {
    MedicationFrequency.BID: (
        time(hour=8, minute=0),
        time(hour=20, minute=0),
    ),
    MedicationFrequency.TDS: (
        time(hour=8, minute=0),
        time(hour=14, minute=0),
        time(hour=20, minute=0),
    ),
    MedicationFrequency.QID: (
        time(hour=0, minute=0),
        time(hour=6, minute=0),
        time(hour=12, minute=0),
        time(hour=18, minute=0),
    ),
}


def generate_schedule(
    *,
    start_at: datetime,
    frequency: MedicationFrequency,
    end_at: datetime | None,
    first_dose_at: datetime | None = None,
) -> list[datetime]:
    """
    Generate scheduled administration times for an inpatient medication.

    Interval-based frequencies are calculated from start_at.

    Daily frequencies use hospital defaults for administration times.
    """

    if frequency in (
        MedicationFrequency.STAT,
        MedicationFrequency.ONCE,
    ):
        if (
            end_at is not None
            and start_at >= end_at
        ):
            return []

        return [start_at]

    interval = FREQUENCY_INTERVALS.get(
        frequency,
    )

    if interval is not None:
        return _generate_interval_schedule(
            start_at=start_at,
            interval=interval,
            end_at=end_at,
        )

    daily_times = DEFAULT_DAILY_TIMES.get(
        frequency,
    )

    if daily_times is None:
        raise ValueError(
            f"Unsupported medication frequency: "
            f"{frequency.value}"
        )

    effective_first_dose = (
        first_dose_at
        if first_dose_at is not None
        else start_at
    )

    scheduled_times: list[datetime] = []

    if (
        end_at is None
        or effective_first_dose < end_at
    ):
        scheduled_times.append(
            effective_first_dose,
        )

    remaining_times = _generate_daily_schedule(
        start_at=effective_first_dose,
        administration_times=daily_times,
        end_at=end_at,
    )

    for scheduled_at in remaining_times:
        if (
            scheduled_at >= effective_first_dose
            and scheduled_at not in scheduled_times
        ):
            scheduled_times.append(
                scheduled_at,
            )

    return scheduled_times


def _generate_interval_schedule(
    *,
    start_at: datetime,
    interval: timedelta,
    end_at: datetime | None,
) -> list[datetime]:
    scheduled_times: list[datetime] = []

    current = start_at

    while (
        end_at is None
        or current < end_at
    ):
        scheduled_times.append(current)
        current += interval

    return scheduled_times


def _generate_daily_schedule(
    *,
    start_at: datetime,
    administration_times: tuple[time, ...],
    end_at: datetime | None,
) -> list[datetime]:
    scheduled_times: list[datetime] = []

    current_date = start_at.date()

    while True:
        for administration_time in administration_times:
            candidate = datetime.combine(
                current_date,
                administration_time,
                tzinfo=start_at.tzinfo,
            )

            if candidate < start_at:
                continue

            if (
                end_at is not None
                and candidate >= end_at
            ):
                return scheduled_times

            scheduled_times.append(candidate)

        if (
            end_at is not None
            and current_date >= end_at.date()
        ):
            break

        current_date += timedelta(days=1)

    return scheduled_times
