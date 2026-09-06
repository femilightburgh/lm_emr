"""add icd11 concept metadata

Revision ID: 7b3c4d5e6f70
Revises: f1a2b3c4d5e6
Create Date: 2026-09-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b3c4d5e6f70"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "terminology_concepts",
        sa.Column(
            "release_version",
            sa.String(length=50),
            nullable=False,
            server_default="2026 Jan",
        ),
    )
    op.add_column(
        "terminology_concepts",
        sa.Column(
            "is_leaf",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "terminology_concepts",
        sa.Column(
            "is_residual",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_index(
        "ix_terminology_concepts_release_version",
        "terminology_concepts",
        ["release_version"],
        unique=False,
    )
    op.create_index(
        "ix_terminology_concepts_is_leaf",
        "terminology_concepts",
        ["is_leaf"],
        unique=False,
    )
    op.create_index(
        "ix_terminology_concepts_is_residual",
        "terminology_concepts",
        ["is_residual"],
        unique=False,
    )

    op.alter_column(
        "terminology_concepts",
        "release_version",
        server_default=None,
    )
    op.alter_column(
        "terminology_concepts",
        "is_leaf",
        server_default=None,
    )
    op.alter_column(
        "terminology_concepts",
        "is_residual",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_terminology_concepts_is_residual",
        table_name="terminology_concepts",
    )
    op.drop_index(
        "ix_terminology_concepts_is_leaf",
        table_name="terminology_concepts",
    )
    op.drop_index(
        "ix_terminology_concepts_release_version",
        table_name="terminology_concepts",
    )

    op.drop_column("terminology_concepts", "is_residual")
    op.drop_column("terminology_concepts", "is_leaf")
    op.drop_column("terminology_concepts", "release_version")
