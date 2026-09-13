"""add permissions module and is_system_permission columns

Revision ID: ae12b3c4d5e6
Revises: 0cd8a0d10b2d
Create Date: 2026-09-06 15:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ae12b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "0cd8a0d10b2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use IF NOT EXISTS to be safe if manual change already applied
    op.execute(
        "ALTER TABLE permissions ADD COLUMN IF NOT EXISTS module varchar(100) NOT NULL DEFAULT 'identity';"
    )
    op.execute(
        "ALTER TABLE permissions ADD COLUMN IF NOT EXISTS is_system_permission boolean NOT NULL DEFAULT false;"
    )
    # remove server defaults to match application expectations
    op.execute("ALTER TABLE permissions ALTER COLUMN module DROP DEFAULT;")
    op.execute("ALTER TABLE permissions ALTER COLUMN is_system_permission DROP DEFAULT;")


def downgrade() -> None:
    # Drop columns if present
    op.execute("ALTER TABLE permissions DROP COLUMN IF EXISTS module;")
    op.execute("ALTER TABLE permissions DROP COLUMN IF EXISTS is_system_permission;")
