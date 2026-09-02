"""
use diagnostic category enum

Revision ID: ec11d6974b57
Revises: 82c68115119e
"""

from typing import Sequence, Union

from alembic import op


revision: str = "ec11d6974b57"
down_revision: Union[str, Sequence[str], None] = "82c68115119e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DIAGNOSTIC_CATEGORY_ENUM = "diagnostic_category_enum"


def upgrade() -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            CREATE TYPE {DIAGNOSTIC_CATEGORY_ENUM} AS ENUM (
                'RADIOLOGY',
                'CARDIOLOGY',
                'NEUROPHYSIOLOGY',
                'RESPIRATORY',
                'AUDIOLOGY',
                'ENDOSCOPY'
            );
        EXCEPTION
            WHEN duplicate_object THEN
                NULL;
        END
        $$;
        """
    )

    op.execute(
        f"""
        ALTER TABLE diagnostic_investigations
        ALTER COLUMN category
        TYPE {DIAGNOSTIC_CATEGORY_ENUM}
        USING category::{DIAGNOSTIC_CATEGORY_ENUM}
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE diagnostic_investigations
        ALTER COLUMN category
        TYPE VARCHAR(50)
        USING category::text
        """
    )

    op.execute(
        f"""
        DROP TYPE IF EXISTS {DIAGNOSTIC_CATEGORY_ENUM}
        """
    )
