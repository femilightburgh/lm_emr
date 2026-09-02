"""
==============================================================================
LIGHTBURGH EMR

Medication Round Service
==============================================================================
"""

from datetime import datetime, timedelta


ROUND_GROUPING_WINDOW = timedelta(
    minutes=30,
)


class MedicationRoundService:
    """
    Groups scheduled medication doses into nursing rounds.
    """

    @staticmethod
    def group_doses(
        *,
        doses,
    ) -> list[list]:
        """
        Group scheduled doses whose times are within 30 minutes.
        """

        if not doses:
            return []

        ordered = sorted(
            doses,
            key=lambda dose: dose.scheduled_at,
        )

        rounds: list[list] = []
        current_round = [ordered[0]]

        for dose in ordered[1:]:
            previous = current_round[-1]

            if (
                dose.scheduled_at
                - previous.scheduled_at
                <= ROUND_GROUPING_WINDOW
            ):
                current_round.append(dose)
            else:
                rounds.append(current_round)
                current_round = [dose]

        rounds.append(current_round)

        return rounds

    @classmethod
    def find_previous_round(
        cls,
        *,
        doses,
        now: datetime,
    ):
        """
        Return the most recent completed round before now.
        """

        rounds = cls.group_doses(
            doses=doses,
        )

        previous_round = None

        for medication_round in rounds:
            round_time = max(
                dose.scheduled_at
                for dose in medication_round
            )

            if round_time <= now:
                previous_round = medication_round
            else:
                break

        return previous_round

    @classmethod
    def find_current_or_next_round(
        cls,
        *,
        doses,
        now: datetime,
    ):
        """
        Return the first round that is currently actionable or upcoming.
        """

        rounds = cls.group_doses(
            doses=doses,
        )

        for medication_round in rounds:
            earliest = min(
                dose.scheduled_at
                for dose in medication_round
            )

            latest = max(
                dose.scheduled_at
                for dose in medication_round
            )

            if (
                latest >= now
                or (
                    earliest <= now
                    and now - latest <= ROUND_GROUPING_WINDOW
                )
            ):
                return medication_round

        return None
