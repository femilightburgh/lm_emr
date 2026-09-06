"""Import ICD-11 MMS terminology data.

This module intentionally separates source validation/parsing from
database persistence. The importer accepts an explicit WHO release
spreadsheet and refuses to proceed when the expected structure is absent.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook


EXPECTED_VERSION = "2026 Jan"
REQUIRED_COLUMNS = {
    "Foundation URI",
    "Linearization URI",
    "Code",
    "Title",
    "ClassKind",
    "DepthInKind",
    "IsResidual",
    "ChapterNo",
    "BrowserLink",
    "isLeaf",
    "Primary tabulation",
    "Parent",
    "Version:2026 Jan 17 - 05:30 UTC",
}


@dataclass(frozen=True)
class ICD11ConceptRow:
    """Validated ICD-11 MMS concept extracted from the release."""

    foundation_uri: str | None
    linearization_uri: str
    code: str
    title: str
    class_kind: str
    depth_in_kind: int | None
    is_residual: bool
    chapter_no: str | None
    browser_link: str | None
    is_leaf: bool
    primary_tabulation: str | None
    parent: str | None
    release_version: str


def normalize_title(title: str) -> str:
    """Remove MMS hierarchy decoration from a WHO title."""

    normalized = re.sub(r"^(?:\s*-\s*)+", "", title.strip())

    if not normalized:
        raise ValueError("ICD-11 title cannot be empty.")

    return normalized


def _required_string(
    value: object,
    *,
    field: str,
    row_number: int,
) -> str:
    if value is None:
        raise ValueError(
            f"Row {row_number}: {field} is required."
        )

    value = str(value).strip()

    if not value:
        raise ValueError(
            f"Row {row_number}: {field} is required."
        )

    return value


def _optional_string(value: object) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _optional_int(
    value: object,
    *,
    field: str,
    row_number: int,
) -> int | None:
    if value is None or str(value).strip() == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Row {row_number}: {field} must be an integer."
        ) from exc


def _required_bool(
    value: object,
    *,
    field: str,
    row_number: int,
) -> bool:
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes"}:
        return True

    if normalized in {"false", "0", "no"}:
        return False

    raise ValueError(
        f"Row {row_number}: {field} must be boolean."
    )


def validate_columns(headers: list[object]) -> None:
    actual = {
        str(header).strip()
        for header in headers
        if header is not None
    }

    missing = REQUIRED_COLUMNS - actual

    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(
            f"ICD-11 source is missing required columns: {missing_text}"
        )


def parse_workbook(path: Path) -> list[ICD11ConceptRow]:
    """Validate and parse an ICD-11 MMS release workbook."""

    if not path.exists():
        raise FileNotFoundError(
            f"ICD-11 source file does not exist: {path}"
        )

    if path.suffix.lower() != ".xlsx":
        raise ValueError(
            "ICD-11 importer requires an .xlsx source file."
        )

    workbook = load_workbook(
        filename=path,
        read_only=True,
        data_only=True,
    )

    try:
        if not workbook.sheetnames:
            raise ValueError(
                "ICD-11 workbook contains no worksheets."
            )

        worksheet = workbook[workbook.sheetnames[0]]

        rows = worksheet.iter_rows(values_only=True)

        try:
            header_row = next(rows)
        except StopIteration as exc:
            raise ValueError(
                "ICD-11 workbook is empty."
            ) from exc

        validate_columns(list(header_row))

        headers = [
            str(header).strip() if header is not None else ""
            for header in header_row
        ]

        positions = {
            header: index
            for index, header in enumerate(headers)
        }

        version_header = next(
            (
                header
                for header in headers
                if header.startswith("Version:")
            ),
            None,
        )

        if version_header is None:
            raise ValueError(
                "ICD-11 workbook is missing its Version: column header."
            )

        release_version = version_header.removeprefix("Version:").strip()

        if EXPECTED_VERSION not in release_version:
            raise ValueError(
                f"Unexpected ICD-11 release version: {release_version!r}"
            )

        concepts: list[ICD11ConceptRow] = []

        for row_number, row in enumerate(rows, start=2):
            if not any(
                value is not None and str(value).strip()
                for value in row
            ):
                continue

            def value(field: str) -> object:
                return row[positions[field]]

            raw_class_kind = value("ClassKind")
            raw_code = value("Code")

            has_class_kind = (
                raw_class_kind is not None
                and str(raw_class_kind).strip()
            )
            has_code = (
                raw_code is not None
                and str(raw_code).strip()
            )

            # WHO MMS contains ancillary rows such as continuation lines for
            # coding notes. These have neither ClassKind nor Code and are not
            # terminology concepts.
            if not has_class_kind and not has_code:
                continue

            if not has_class_kind and has_code:
                raise ValueError(
                    f"Row {row_number}: Code is present but ClassKind is "
                    "missing."
                )

            class_kind = _required_string(
                raw_class_kind,
                field="ClassKind",
                row_number=row_number,
            )

            if class_kind not in {"chapter", "block", "category"}:
                raise ValueError(
                    f"Row {row_number}: unsupported ICD-11 ClassKind "
                    f"{class_kind!r}."
                )

            # WHO MMS chapter and block rows are hierarchy-only and do not
            # carry a selectable ICD-11 code. Import coded category concepts.
            if class_kind != "category":
                continue

            linearization_uri = _required_string(
                value("Linearization URI"),
                field="Linearization URI",
                row_number=row_number,
            )

            code = _required_string(
                value("Code"),
                field="Code",
                row_number=row_number,
            )

            raw_title = _required_string(
                value("Title"),
                field="Title",
                row_number=row_number,
            )

            concepts.append(
                ICD11ConceptRow(
                    foundation_uri=_optional_string(
                        value("Foundation URI"),
                    ),
                    linearization_uri=linearization_uri,
                    code=code,
                    title=normalize_title(raw_title),
                    class_kind=_required_string(
                        value("ClassKind"),
                        field="ClassKind",
                        row_number=row_number,
                    ),
                    depth_in_kind=_optional_int(
                        value("DepthInKind"),
                        field="DepthInKind",
                        row_number=row_number,
                    ),
                    is_residual=_required_bool(
                        value("IsResidual"),
                        field="IsResidual",
                        row_number=row_number,
                    ),
                    chapter_no=_optional_string(
                        value("ChapterNo"),
                    ),
                    browser_link=_optional_string(
                        value("BrowserLink"),
                    ),
                    is_leaf=_required_bool(
                        value("isLeaf"),
                        field="isLeaf",
                        row_number=row_number,
                    ),
                    primary_tabulation=_optional_string(
                        value("Primary tabulation"),
                    ),
                    parent=_optional_string(
                        value("Parent"),
                    ),
                    release_version=release_version,
                ),
            )

        if not concepts:
            raise ValueError(
                "ICD-11 workbook contains no concept rows."
            )

        return concepts

    finally:
        workbook.close()


def validate_concepts(
    concepts: list[ICD11ConceptRow],
) -> tuple[int, int]:
    """Validate dataset-level invariants after workbook parsing."""

    if not concepts:
        raise ValueError(
            "ICD-11 concept dataset is empty."
        )

    codes: set[str] = set()
    linearization_uris: set[str] = set()

    leaf_count = 0
    non_leaf_count = 0

    expected_release = concepts[0].release_version

    if EXPECTED_VERSION not in expected_release:
        raise ValueError(
            f"Unexpected ICD-11 release version: {expected_release!r}"
        )

    for index, concept in enumerate(concepts, start=1):
        if concept.class_kind != "category":
            raise ValueError(
                f"Concept {index} ({concept.code}): expected ClassKind "
                f"'category', got {concept.class_kind!r}."
            )

        if not concept.code:
            raise ValueError(
                f"Concept {index}: ICD-11 code is empty."
            )

        if concept.code in codes:
            raise ValueError(
                f"Duplicate ICD-11 code detected: {concept.code!r}."
            )
        codes.add(concept.code)

        if not concept.title:
            raise ValueError(
                f"Concept {index} ({concept.code}): title is empty."
            )

        if not concept.linearization_uri:
            raise ValueError(
                f"Concept {index} ({concept.code}): "
                "Linearization URI is empty."
            )

        if concept.linearization_uri in linearization_uris:
            raise ValueError(
                "Duplicate ICD-11 Linearization URI detected: "
                f"{concept.linearization_uri!r}."
            )
        linearization_uris.add(concept.linearization_uri)

        if not concept.linearization_uri.startswith(
            "http://id.who.int/icd/release/11/mms/"
        ):
            raise ValueError(
                f"Concept {index} ({concept.code}): unexpected "
                f"Linearization URI: {concept.linearization_uri!r}."
            )

        if concept.foundation_uri is not None and not concept.foundation_uri.startswith(
            "http://id.who.int/icd/entity/"
        ):
            raise ValueError(
                f"Concept {index} ({concept.code}): unexpected "
                f"Foundation URI: {concept.foundation_uri!r}."
            )

        if concept.parent is not None and not concept.parent.startswith(
            "http://id.who.int/icd/entity/"
        ):
            raise ValueError(
                f"Concept {index} ({concept.code}): unexpected "
                f"Parent URI: {concept.parent!r}."
            )

        if concept.release_version != expected_release:
            raise ValueError(
                f"Concept {index} ({concept.code}): release version "
                f"{concept.release_version!r} differs from "
                f"{expected_release!r}."
            )

        if concept.is_leaf:
            leaf_count += 1
        else:
            non_leaf_count += 1

    return leaf_count, non_leaf_count


def import_concepts(
    concepts: list[ICD11ConceptRow],
) -> int:
    """Persist a validated ICD-11 concept dataset atomically."""

    from sqlalchemy import func, insert, select

    from app.db.session import SessionLocal
    from app.modules.terminology.enums import TerminologySystem
    from app.modules.terminology.models import TerminologyConcept

    if not concepts:
        raise ValueError(
            "Cannot import an empty ICD-11 concept dataset."
        )

    release_version = concepts[0].release_version

    db = SessionLocal()

    try:
        with db.begin():
            existing_count = db.scalar(
                select(func.count(TerminologyConcept.id)).where(
                    TerminologyConcept.system == TerminologySystem.ICD_11,
                    TerminologyConcept.release_version == release_version,
                )
            )

            if existing_count:
                raise RuntimeError(
                    f"ICD-11 release {release_version!r} already contains "
                    f"{existing_count} terminology concepts. "
                    "Import refused to prevent duplicate or destructive loading."
                )

            rows = [
                {
                    "system": TerminologySystem.ICD_11,
                    "code": concept.code,
                    "display_name": concept.title,
                    "description": None,
                    "uri": concept.linearization_uri,
                    "release_version": concept.release_version,
                    "is_leaf": concept.is_leaf,
                    "is_residual": concept.is_residual,
                    "active": True,
                }
                for concept in concepts
            ]

            batch_size = 1000

            for start in range(0, len(rows), batch_size):
                batch = rows[start : start + batch_size]

                db.execute(
                    insert(TerminologyConcept),
                    batch,
                )

            imported_count = db.scalar(
                select(func.count(TerminologyConcept.id)).where(
                    TerminologyConcept.system == TerminologySystem.ICD_11,
                    TerminologyConcept.release_version == release_version,
                )
            )

            if imported_count != len(concepts):
                raise RuntimeError(
                    f"ICD-11 import verification failed: expected "
                    f"{len(concepts)} concepts, found {imported_count}."
                )

        return imported_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and parse an ICD-11 MMS release workbook.",
    )

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Path to the WHO ICD-11 MMS .xlsx release file.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    concepts = parse_workbook(args.source)
    leaf_count, non_leaf_count = validate_concepts(concepts)

    print(f"✓ Validated ICD-11 release: {EXPECTED_VERSION}")
    print(f"✓ Parsed concepts: {len(concepts)}")
    print(f"✓ Validated unique codes: {len(concepts)}")
    print(f"✓ Validated unique Linearization URIs: {len(concepts)}")
    print(f"✓ Leaf concepts: {leaf_count}")
    print(f"✓ Non-leaf concepts: {non_leaf_count}")
    print(f"✓ First concept: {concepts[0].code} — {concepts[0].title}")

    print()
    print("Importing validated concepts into the database...")

    imported_count = import_concepts(concepts)

    print(f"✓ Imported concepts: {imported_count}")


if __name__ == "__main__":
    main()
