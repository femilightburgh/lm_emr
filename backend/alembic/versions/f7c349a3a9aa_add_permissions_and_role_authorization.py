"""add permissions and role authorization

Revision ID: f7c349a3a9aa
Revises: bda631ee8e89
Create Date: 2026-08-05 12:04:28.914302

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f7c349a3a9aa"
down_revision: Union[str, Sequence[str], None] = "bda631ee8e89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema.
    """

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------

    op.add_column(
        "permissions",
        sa.Column(
            "is_platform_permission",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.alter_column(
        "permissions",
        "is_platform_permission",
        server_default=None,
    )

    op.drop_index(
        op.f("ix_permissions_code"),
        table_name="permissions",
    )

    op.create_index(
        op.f("ix_permissions_code"),
        "permissions",
        ["code"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_permission_code",
        "permissions",
        ["code"],
    )

    op.drop_column(
        "permissions",
        "module",
    )

    op.drop_column(
        "permissions",
        "is_system_permission",
    )

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------

    op.add_column(
        "roles",
        sa.Column(
            "is_template",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.alter_column(
        "roles",
        "is_template",
        server_default=None,
    )

    op.drop_column(
        "roles",
        "is_system_role",
    )


def downgrade() -> None:
    """
    Downgrade schema.
    """

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------

    op.add_column(
        "roles",
        sa.Column(
            "is_system_role",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.alter_column(
        "roles",
        "is_system_role",
        server_default=None,
    )

    op.drop_column(
        "roles",
        "is_template",
    )

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------

    op.add_column(
        "permissions",
        sa.Column(
            "is_system_permission",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.alter_column(
        "permissions",
        "is_system_permission",
        server_default=None,
    )

    op.add_column(
        "permissions",
        sa.Column(
            "module",
            sa.String(length=100),
            nullable=False,
            server_default="identity",
        ),
    )

    op.alter_column(
        "permissions",
        "module",
        server_default=None,
    )

    op.drop_constraint(
        "uq_permission_code",
        "permissions",
        type_="unique",
    )

    op.drop_index(
        op.f("ix_permissions_code"),
        table_name="permissions",
    )

    op.create_index(
        op.f("ix_permissions_code"),
        "permissions",
        ["code"],
        unique=True,
    )

    op.drop_column(
        "permissions",
        "is_platform_permission",
    )