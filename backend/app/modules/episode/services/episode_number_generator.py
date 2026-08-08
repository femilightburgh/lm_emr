"""
==============================================================================
LIGHTBURGH EMR

Episode Number Generator

==============================================================================

Purpose
-------

Generates human-readable Episode numbers within a Hospital.

Format:

    EPI-00000001
    EPI-00000002
    EPI-00000003

Episode numbers are scoped to the Hospital.

==============================================================================
"""

from uuid import UUID

from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)


class EpisodeNumberGenerator:
    """
    Generates the next Episode number for a Hospital.
    """

    PREFIX = "EPI"
    STARTING_NUMBER = 1
    NUMBER_WIDTH = 8

    def __init__(
        self,
        repository: EpisodeRepository,
    ) -> None:
        self.repository = repository

    def generate(
        self,
        *,
        hospital_id: UUID,
    ) -> str:
        """
        Generate the next Episode number for a Hospital.
        """

        latest_number = self.repository.get_latest_episode_number(
            hospital_id=hospital_id,
        )

        if latest_number is None:
            next_number = self.STARTING_NUMBER
        else:
            next_number = self._extract_sequence(
                latest_number,
            ) + 1

        return self._format(
            next_number,
        )

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _extract_sequence(
        self,
        episode_number: str,
    ) -> int:
        """
        Extract the numeric sequence from an Episode number.

        Example:

            EPI-00000027 → 27
        """

        prefix = f"{self.PREFIX}-"

        if not episode_number.startswith(prefix):
            raise ValueError(
                f"Invalid Episode number format: {episode_number}",
            )

        numeric_part = episode_number.removeprefix(
            prefix,
        )

        if not numeric_part.isdigit():
            raise ValueError(
                f"Invalid Episode number format: {episode_number}",
            )

        return int(numeric_part)

    def _format(
        self,
        sequence: int,
    ) -> str:
        """
        Format a sequence number into the standard Episode number.
        """

        return (
            f"{self.PREFIX}-"
            f"{sequence:0{self.NUMBER_WIDTH}d}"
        )