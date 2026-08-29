"""add structured laboratory analytes and result values

Revision ID: 2939eeaa93fb
Revises: 0f2046a9aa21
Create Date: 2026-08-27 16:50:43.612163

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "2939eeaa93fb"
down_revision: Union[str, Sequence[str], None] = "0f2046a9aa21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ANALYTE_DATA_TYPE_ENUM = "laboratory_analyte_data_type_enum"


def upgrade() -> None:
    bind = op.get_bind()

    analyte_data_type_enum = postgresql.ENUM(
        "NUMERIC",
        "TEXT",
        "BOOLEAN",
        "CODED",
        name=ANALYTE_DATA_TYPE_ENUM,
    )

    analyte_data_type_enum.create(
        bind,
        checkfirst=True,
    )

    op.create_table(
        "laboratory_test_analytes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "laboratory_test_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "data_type",
            postgresql.ENUM(
                "NUMERIC",
                "TEXT",
                "BOOLEAN",
                "CODED",
                name=ANALYTE_DATA_TYPE_ENUM,
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "reference_low",
            sa.Numeric(),
            nullable=True,
        ),
        sa.Column(
            "reference_high",
            sa.Numeric(),
            nullable=True,
        ),
        sa.Column(
            "reference_text",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "options",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.ForeignKeyConstraint(
            ["laboratory_test_id"],
            ["laboratory_tests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "laboratory_test_id",
            "code",
            name="uq_laboratory_test_analyte_code",
        ),
    )

    op.create_index(
        "ix_laboratory_test_analytes_laboratory_test_id",
        "laboratory_test_analytes",
        ["laboratory_test_id"],
    )

    op.create_table(
        "clinical_result_values",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "clinical_result_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "analyte_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "value_numeric",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "value_text",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "value_boolean",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "value_code",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "abnormal_flag",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "comment",
            sa.Text(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["clinical_result_id"],
            ["clinical_results.id"],
        ),
        sa.ForeignKeyConstraint(
            ["analyte_id"],
            ["laboratory_test_analytes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinical_result_id",
            "analyte_id",
            name="uq_clinical_result_value_analyte",
        ),
    )

    op.create_index(
        "ix_clinical_result_values_clinical_result_id",
        "clinical_result_values",
        ["clinical_result_id"],
    )

    op.create_index(
        "ix_clinical_result_values_analyte_id",
        "clinical_result_values",
        ["analyte_id"],
    )

    op.add_column(
        "clinical_results",
        sa.Column(
            "specimen",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "clinical_results",
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "clinical_results",
        sa.Column(
            "reported_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "clinical_results",
        sa.Column(
            "interpretation",
            sa.Text(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # Backfill analytes from the existing laboratory catalogue.
    # ------------------------------------------------------------------

    laboratory_rows = bind.execute(
        sa.text(
            """
            SELECT
                id,
                result_fields
            FROM laboratory_tests
            WHERE result_fields IS NOT NULL
            """
        )
    ).mappings()

    from uuid import uuid4
    from datetime import UTC, datetime
    import json

    now = datetime.now(UTC)

    for row in laboratory_rows:
        result_fields = row["result_fields"]

        if not isinstance(result_fields, dict):
            continue

        for display_order, (code, definition) in enumerate(
            result_fields.items()
        ):
            if not isinstance(definition, dict):
                continue

            raw_type = definition.get("type", "text")

            data_type = {
                "number": "NUMERIC",
                "numeric": "NUMERIC",
                "text": "TEXT",
                "select": "CODED",
                "coded": "CODED",
                "boolean": "BOOLEAN",
            }.get(
                str(raw_type).lower(),
                "TEXT",
            )

            bind.execute(
                sa.text(
                    """
                    INSERT INTO laboratory_test_analytes (
                        id,
                        created_at,
                        updated_at,
                        laboratory_test_id,
                        code,
                        name,
                        data_type,
                        unit,
                        reference_low,
                        reference_high,
                        reference_text,
                        options,
                        required,
                        display_order
                    )
                    VALUES (
                        :id,
                        :created_at,
                        :updated_at,
                        :laboratory_test_id,
                        :code,
                        :name,
                        :data_type,
                        :unit,
                        :reference_low,
                        :reference_high,
                        :reference_text,
                        CAST(:options AS JSON),
                        :required,
                        :display_order
                    )
                    """
                ),
                {
                    "id": uuid4(),
                    "created_at": now,
                    "updated_at": now,
                    "laboratory_test_id": row["id"],
                    "code": str(code),
                    "name": str(
                        definition.get(
                            "label",
                            code,
                        )
                    ),
                    "data_type": data_type,
                    "unit": definition.get("unit"),
                    "reference_low": definition.get("reference_low"),
                    "reference_high": definition.get("reference_high"),
                    "reference_text": definition.get("reference_text"),
                    "options": json.dumps(
                        definition.get("options")
                    )
                    if definition.get("options") is not None
                    else None,
                    "required": bool(
                        definition.get(
                            "required",
                            False,
                        )
                    ),
                    "display_order": display_order,
                },
            )

    # ------------------------------------------------------------------
    # Backfill structured result values.
    #
    # Existing orders identify the laboratory test through details.test_code.
    # Existing result_data keys map to analyte codes.
    # ------------------------------------------------------------------

    result_rows = bind.execute(
        sa.text(
            """
            SELECT
                cr.id AS clinical_result_id,
                cr.result_data,
                co.details,
                co.order_type
            FROM clinical_results cr
            JOIN clinical_orders co
              ON co.id = cr.order_id
            WHERE cr.result_type = 'LABORATORY'
            """
        )
    ).mappings()

    for row in result_rows:
        details = row["details"]
        result_data = row["result_data"]

        if not isinstance(details, dict):
            continue

        if not isinstance(result_data, dict):
            continue

        test_code = details.get("test_code")

        if not isinstance(test_code, str) or not test_code.strip():
            continue

        analytes = bind.execute(
            sa.text(
                """
                SELECT
                    lta.id,
                    lta.code,
                    lta.data_type
                FROM laboratory_test_analytes lta
                JOIN laboratory_tests lt
                  ON lt.id = lta.laboratory_test_id
                WHERE lt.code = :test_code
                """
            ),
            {
                "test_code": test_code,
            },
        ).mappings()

        analyte_by_code = {
            item["code"]: item
            for item in analytes
        }

        for key, value in result_data.items():
            analyte = analyte_by_code.get(str(key))

            if analyte is None:
                continue

            value_numeric = None
            value_text = None
            value_boolean = None
            value_code = None

            data_type = analyte["data_type"]

            if data_type == "NUMERIC":
                try:
                    value_numeric = float(value)
                except (TypeError, ValueError):
                    value_text = str(value)
            elif data_type == "BOOLEAN":
                if isinstance(value, bool):
                    value_boolean = value
                else:
                    value_text = str(value)
            elif data_type == "CODED":
                value_code = str(value)
            else:
                value_text = str(value)

            bind.execute(
                sa.text(
                    """
                    INSERT INTO clinical_result_values (
                        id,
                        created_at,
                        updated_at,
                        clinical_result_id,
                        analyte_id,
                        value_numeric,
                        value_text,
                        value_boolean,
                        value_code
                    )
                    VALUES (
                        :id,
                        :created_at,
                        :updated_at,
                        :clinical_result_id,
                        :analyte_id,
                        :value_numeric,
                        :value_text,
                        :value_boolean,
                        :value_code
                    )
                    ON CONFLICT (
                        clinical_result_id,
                        analyte_id
                    ) DO NOTHING
                    """
                ),
                {
                    "id": uuid4(),
                    "created_at": now,
                    "updated_at": now,
                    "clinical_result_id": row["clinical_result_id"],
                    "analyte_id": analyte["id"],
                    "value_numeric": value_numeric,
                    "value_text": value_text,
                    "value_boolean": value_boolean,
                    "value_code": value_code,
                },
            )


def downgrade() -> None:
    op.drop_column(
        "clinical_results",
        "interpretation",
    )

    op.drop_column(
        "clinical_results",
        "reported_at",
    )

    op.drop_column(
        "clinical_results",
        "collected_at",
    )

    op.drop_column(
        "clinical_results",
        "specimen",
    )

    op.drop_index(
        "ix_clinical_result_values_analyte_id",
        table_name="clinical_result_values",
    )

    op.drop_index(
        "ix_clinical_result_values_clinical_result_id",
        table_name="clinical_result_values",
    )

    op.drop_table("clinical_result_values")

    op.drop_index(
        "ix_laboratory_test_analytes_laboratory_test_id",
        table_name="laboratory_test_analytes",
    )

    op.drop_table("laboratory_test_analytes")

    analyte_data_type_enum = postgresql.ENUM(
        "NUMERIC",
        "TEXT",
        "BOOLEAN",
        "CODED",
        name=ANALYTE_DATA_TYPE_ENUM,
    )

    analyte_data_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
