"""
==============================================================================
LIGHTBURGH EMR

Local File Storage
==============================================================================
"""

from pathlib import Path
from uuid import uuid4


class LocalStorage:
    """
    Stores application files on the local filesystem.
    """

    def __init__(
        self,
        root_path: str,
    ) -> None:
        self.root = Path(root_path).resolve()

    def save(
        self,
        *,
        content: bytes,
        original_filename: str,
        prefix: str = "diagnostics",
    ) -> str:
        directory = self.root / prefix
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        suffix = Path(original_filename).suffix.lower()

        storage_key = (
            f"{prefix}/"
            f"{uuid4().hex}"
            f"{suffix}"
        )

        target = self._resolve(
            storage_key,
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_bytes(content)

        return storage_key

    def read(
        self,
        *,
        storage_key: str,
    ) -> bytes:
        return self._resolve(
            storage_key,
        ).read_bytes()

    def delete(
        self,
        *,
        storage_key: str,
    ) -> None:
        path = self._resolve(
            storage_key,
        )

        if path.exists():
            path.unlink()

    def exists(
        self,
        *,
        storage_key: str,
    ) -> bool:
        return self._resolve(
            storage_key,
        ).exists()

    def _resolve(
        self,
        storage_key: str,
    ) -> Path:
        candidate = (
            self.root / storage_key
        ).resolve()

        if (
            candidate != self.root
            and self.root not in candidate.parents
        ):
            raise ValueError(
                "Invalid storage key.",
            )

        return candidate
