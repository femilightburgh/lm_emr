"""
==============================================================================
LIGHTBURGH EMR

Scope Laboratory Tests by Hospital
==============================================================================
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "21521b547900"
down_revision: Union[str, Sequence[str], None] = "d49d5295ce72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Scope laboratory test catalogue entries by hospital.

    The original laboratory catalogue was global and was created before
    hospital ownership was introduced.

    Existing catalogue data is legacy development/test data. Remove the
    dependent legacy laboratory results first, then remove the catalogue.
    New hospital-scoped catalogue entries are created by the application
    bootstrap process.
    """

    # ------------------------------------------------------------------
    # Remove legacy clinical result values belonging to the old
    # laboratory catalogue.
    # ------------------------------------------------------------------

    op.execute(
        sa.text(
            """
            DELETE FROM clinical_result_values
            WHERE analyte_id IN (
                SELECT lta.id
                FROM laboratory_test_analytes lta
                JOIN laboratory_tests lt
                    ON lt.id = lta.laboratory_test_id
            )
            """
        )
    )

    # ------------------------------------------------------------------
    # Remove clinical results that belonged to the legacy laboratory
    # catalogue.
    #
    # At this stage the legacy laboratory result values have already
    # been removed. The clinical results are identified through their
    # laboratory orders.
    # ------------------------------------------------------------------

    op.execute(
        sa.text(
            """
            DELETE FROM clinical_results
            WHERE order_id IN (
                SELECT id
                FROM clinical_orders
                WHERE order_type = 'LABORATORY'
                  AND details ->> 'test_code' IN (
                      SELECT code
                      FROM laboratory_tests
                  )
            )
            """
        )
    )

    # ------------------------------------------------------------------
    # Remove legacy laboratory analytes.
    # ------------------------------------------------------------------

    op.execute(
        sa.text(
            """
            DELETE FROM laboratory_test_analytes
            WHERE laboratory_test_id IN (
                SELECT id
                FROM laboratory_tests
            )
            """
        )
    )

    # ------------------------------------------------------------------
    # Remove legacy global laboratory tests.
    # ------------------------------------------------------------------

    op.execute(
        sa.text(
            """
            DELETE FROM laboratory_tests
            """
        )
    )

    # ------------------------------------------------------------------
    # Add hospital ownership.
    # ------------------------------------------------------------------

    op.add_column(
        "laboratory_tests",
        sa.Column(
            "hospital_id",
            sa.UUID(),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # Replace global uniqueness with hospital-scoped uniqueness.
    # ------------------------------------------------------------------

    op.drop_constraint(
        op.f("uq_laboratory_test_code"),
        "laboratory_tests",
        type_="unique",
    )

    op.create_index(
        op.f("ix_laboratory_tests_hospital_id"),
        "laboratory_tests",
        ["hospital_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_laboratory_test_hospital_code",
        "laboratory_tests",
        ["hospital_id", "code"],
    )

    op.create_foreign_key(
        "fk_laboratory_tests_hospital_id_hospitals",
        "laboratory_tests",
        "hospitals",
        ["hospital_id"],
        ["id"],
    )


def downgrade() -> None:
    """
    Reverse the hospital-scoping schema change.

    Catalogue records created after this migration cannot be safely
    converted back into a single global catalogue automatically.
    """

    op.drop_constraint(
        "fk_laboratory_tests_hospital_id_hospitals",
        "laboratory_tests",
        type_="foreignkey",
    )

    op.drop_constraint(
        "uq_laboratory_test_hospital_code",
        "laboratory_tests",
        type_="unique",
    )

    op.drop_index(
        op.f("ix_laboratory_tests_hospital_id"),
        table_name="laboratory_tests",
    )

    op.create_unique_constraint(
        op.f("uq_laboratory_test_code"),
        "laboratory_tests",
        ["code"],
    )

    op.drop_column(
        "laboratory_tests",
        "hospital_id",
    )
