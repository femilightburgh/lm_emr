"""repair malformed laboratory orders

Revision ID: bb5c652bb168
Revises: d0cc3e2e04f7
"""

from typing import Sequence, Union

from alembic import op


revision: str = "bb5c652bb168"
down_revision: Union[str, Sequence[str], None] = "d0cc3e2e04f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE clinical_orders
        SET details = jsonb_set(
            jsonb_set(
                details::jsonb,
                '{test_code}',
                '"EUCR"'
            ),
            '{test_name}',
            '"Electrolytes, Urea and Creatinine"'
        )::json
        WHERE order_type = 'LABORATORY'
          AND status IN (
              'REQUESTED',
              'RECEIVED',
              'IN_PROGRESS'
          )
          AND lower(details->>'test_code') = 'uecr'
        """
    )

    op.execute(
        """
        UPDATE clinical_orders
        SET details = jsonb_set(
            jsonb_set(
                details::jsonb,
                '{test_code}',
                '"MALARIA"'
            ),
            '{test_name}',
            '"Malaria Test"'
        )::json
        WHERE order_type = 'LABORATORY'
          AND status IN (
              'REQUESTED',
              'RECEIVED',
              'IN_PROGRESS'
          )
          AND lower(details->>'test_code') = 'mp'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE clinical_orders
        SET details = jsonb_set(
            jsonb_set(
                details::jsonb,
                '{test_code}',
                '"UECr"'
            ),
            '{test_name}',
            '"Renal function test"'
        )::json
        WHERE order_type = 'LABORATORY'
          AND status IN (
              'REQUESTED',
              'RECEIVED',
              'IN_PROGRESS'
          )
          AND details->>'test_code' = 'EUCR'
          AND details->>'test_name' =
              'Electrolytes, Urea and Creatinine'
        """
    )

    op.execute(
        """
        UPDATE clinical_orders
        SET details = jsonb_set(
            jsonb_set(
                details::jsonb,
                '{test_code}',
                '"MP"'
            ),
            '{test_name}',
            '"Malaria test"'
        )::json
        WHERE order_type = 'LABORATORY'
          AND status IN (
              'REQUESTED',
              'RECEIVED',
              'IN_PROGRESS'
          )
          AND details->>'test_code' = 'MALARIA'
          AND details->>'test_name' = 'Malaria Test'
        """
    )
