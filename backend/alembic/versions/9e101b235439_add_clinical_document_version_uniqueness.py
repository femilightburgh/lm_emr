"""
==============================================================================
LIGHTBURGH EMR

Add Clinical Document Version Uniqueness
==============================================================================

Ensures that Clinical Document version numbers are unique within an
Encounter and Clinical Document type.

Invariant
---------

For a given:

    encounter_id
    document_type

there may be only one row for each version number.

Example:

    INITIAL_CLERKING v1    allowed
    INITIAL_CLERKING v2    allowed
    INITIAL_CLERKING v2    forbidden

    PROGRESS_NOTE v1       allowed

The constraint protects document version integrity at the database level,
including against concurrent amendment requests.
==============================================================================
"""

from typing import Sequence, Union

from alembic import op


# =============================================================================
# Revision identifiers
# =============================================================================

revision: str = "9e101b235439"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "c04993ca379b"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =============================================================================
# Upgrade
# =============================================================================


def upgrade() -> None:
    """
    Enforce unique Clinical Document versions per Encounter and document type.
    """

    op.create_unique_constraint(
        "uq_clinical_documents_encounter_type_version",
        "clinical_documents",
        [
            "encounter_id",
            "document_type",
            "version",
        ],
    )


# =============================================================================
# Downgrade
# =============================================================================


def downgrade() -> None:
    """
    Remove the Clinical Document version uniqueness constraint.
    """

    op.drop_constraint(
        "uq_clinical_documents_encounter_type_version",
        "clinical_documents",
        type_="unique",
    )