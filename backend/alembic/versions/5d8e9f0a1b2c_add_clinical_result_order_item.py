"""add clinical result order item

Revision ID: 5d8e9f0a1b2c
Revises: 47c67dab84c1
Create Date: 2026-09-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d8e9f0a1b2c"
down_revision: Union[str, Sequence[str], None] = "47c67dab84c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # Add the new nullable relationship first.  Existing order_id remains
    # intact during the transition.
    # -----------------------------------------------------------------------
    op.add_column(
        "clinical_results",
        sa.Column(
            "order_item_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_clinical_results_order_item_id",
        "clinical_results",
        ["order_item_id"],
    )

    op.create_foreign_key(
        "fk_clinical_results_order_item_id",
        "clinical_results",
        "clinical_order_items",
        ["order_item_id"],
        ["id"],
    )

    # -----------------------------------------------------------------------
    # Backfill legacy laboratory results.
    #
    # Legacy laboratory orders stored their catalogue code in:
    #     clinical_orders.details["test_code"]
    #
    # Create one ClinicalOrderItem for each legacy laboratory order that
    # contains a test_code and does not already have an item.
    #
    # Hospital scope is enforced when resolving LaboratoryTest.
    # -----------------------------------------------------------------------

    bind = op.get_bind()

    legacy_orders = bind.execute(
        sa.text("""
            SELECT
                co.id AS order_id,
                ep.hospital_id,
                CAST(co.details AS jsonb)->>'test_code' AS test_code
            FROM clinical_orders co
            JOIN encounters e
              ON e.id = co.encounter_id
            JOIN episodes ep
              ON ep.id = e.episode_id
            WHERE co.order_type = 'LABORATORY'
              AND CAST(co.details AS jsonb)->>'test_code' IS NOT NULL
              AND CAST(co.details AS jsonb)->>'test_code' <> 'ECG'
              AND NOT EXISTS (
                  SELECT 1
                  FROM clinical_order_items coi
                  WHERE coi.clinical_order_id = co.id
              )
            ORDER BY co.created_at, co.id
        """)
    ).mappings().all()

    for display_order, row in enumerate(legacy_orders):
        test = bind.execute(
            sa.text("""
                SELECT
                    id,
                    code,
                    name
                FROM laboratory_tests
                WHERE hospital_id = :hospital_id
                  AND code = :test_code
                LIMIT 1
            """),
            {
                "hospital_id": row["hospital_id"],
                "test_code": row["test_code"],
            },
        ).mappings().first()

        if test is None:
            raise RuntimeError(
                "Cannot migrate legacy laboratory order "
                f"{row['order_id']}: laboratory test "
                f"{row['test_code']!r} was not found for hospital "
                f"{row['hospital_id']}."
            )

        item_id = bind.execute(
            sa.text("""
                SELECT gen_random_uuid()
            """)
        ).scalar_one()

        bind.execute(
            sa.text("""
                INSERT INTO clinical_order_items (
                    clinical_order_id,
                    item_type,
                    status,
                    laboratory_test_id,
                    diagnostic_investigation_id,
                    display_order,
                    details,
                    id,
                    created_at,
                    updated_at
                )
                SELECT
                    :order_id,
                    'LABORATORY'::clinical_order_item_type_enum,
                    CAST(co.status::text AS clinical_order_item_status_enum),
                    CAST(:laboratory_test_id AS uuid),
                    CAST(NULL AS uuid),
                    0,
                    json_build_object(
                        'test_code', CAST(:test_code AS text),
                        'test_name', CAST(:test_name AS text)
                    ),
                    :item_id,
                    co.created_at,
                    co.updated_at
                FROM clinical_orders co
                WHERE co.id = :order_id
            """),
            {
                "order_id": row["order_id"],
                "laboratory_test_id": test["id"],
                "test_code": test["code"],
                "test_name": test["name"],
                "item_id": item_id,
            },
        )

    # -----------------------------------------------------------------------
    # Attach legacy results to the corresponding newly-created item.
    # -----------------------------------------------------------------------

    bind.execute(
        sa.text("""
            UPDATE clinical_results cr
            SET order_item_id = coi.id
            FROM clinical_orders co
            JOIN clinical_order_items coi
              ON coi.clinical_order_id = co.id
             AND coi.item_type = 'LABORATORY'
            JOIN encounters e
              ON e.id = co.encounter_id
            JOIN episodes ep
              ON ep.id = e.episode_id
            JOIN laboratory_tests lt
              ON lt.id = coi.laboratory_test_id
            WHERE cr.order_id = co.id
              AND cr.order_item_id IS NULL
              AND co.order_type = 'LABORATORY'
              AND lt.code = CAST(co.details AS jsonb)->>'test_code'
              AND lt.hospital_id = ep.hospital_id
        """)
    )

    # -----------------------------------------------------------------------
    # Hard safety check: every existing ClinicalResult must now have an item.
    # -----------------------------------------------------------------------

    unmapped = bind.execute(
        sa.text("""
            SELECT COUNT(*)
            FROM clinical_results
            WHERE order_item_id IS NULL
        """)
    ).scalar_one()

    if unmapped:
        raise RuntimeError(
            f"ClinicalResult migration left {unmapped} result(s) "
            "without an order_item_id."
        )


def downgrade() -> None:
    op.drop_constraint(
        "fk_clinical_results_order_item_id",
        "clinical_results",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_clinical_results_order_item_id",
        table_name="clinical_results",
    )

    op.drop_column(
        "clinical_results",
        "order_item_id",
    )
