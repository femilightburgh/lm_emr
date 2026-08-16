"""create clinical documents

Revision ID: 85da5ea9d7df
Revises: 085a487a923f
Create Date: 2026-08-15 18:25:25.377296

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "85da5ea9d7df"
down_revision: Union[str, Sequence[str], None] = "085a487a923f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create the Clinical Documents table.
    """

    op.create_table(
        "clinical_documents",

        sa.Column(
            "encounter_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "document_type",
            sa.Enum(
                "INITIAL_CLERKING",
                "PROGRESS_NOTE",
                "DISCHARGE_SUMMARY",
                name="clinical_document_type_enum",
            ),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SIGNED",
                name="clinical_document_status_enum",
            ),
            nullable=False,
        ),

        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "content",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "authored_by",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "signed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "signed_by",
            sa.UUID(),
            nullable=True,
        ),

        sa.Column(
            "amended_from_id",
            sa.UUID(),
            nullable=True,
        ),

        sa.Column(
            "id",
            sa.UUID(),
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

        # ------------------------------------------------------------------
        # Foreign Keys
        # ------------------------------------------------------------------

        sa.ForeignKeyConstraint(
            ["encounter_id"],
            ["encounters.id"],
        ),

        sa.ForeignKeyConstraint(
            ["authored_by"],
            ["staff.id"],
        ),

        sa.ForeignKeyConstraint(
            ["signed_by"],
            ["staff.id"],
        ),

        sa.ForeignKeyConstraint(
            ["amended_from_id"],
            ["clinical_documents.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    # ----------------------------------------------------------------------
    # Indexes
    # ----------------------------------------------------------------------

    op.create_index(
        "ix_clinical_documents_amended_from_id",
        "clinical_documents",
        ["amended_from_id"],
        unique=False,
    )

    op.create_index(
        "ix_clinical_documents_authored_by",
        "clinical_documents",
        ["authored_by"],
        unique=False,
    )

    op.create_index(
        "ix_clinical_documents_document_type",
        "clinical_documents",
        ["document_type"],
        unique=False,
    )

    op.create_index(
        "ix_clinical_documents_encounter_id",
        "clinical_documents",
        ["encounter_id"],
        unique=False,
    )

    op.create_index(
        "ix_clinical_documents_signed_by",
        "clinical_documents",
        ["signed_by"],
        unique=False,
    )

    op.create_index(
        "ix_clinical_documents_status",
        "clinical_documents",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """
    Remove the Clinical Documents table.
    """

    op.drop_index(
        "ix_clinical_documents_status",
        table_name="clinical_documents",
    )

    op.drop_index(
        "ix_clinical_documents_signed_by",
        table_name="clinical_documents",
    )

    op.drop_index(
        "ix_clinical_documents_encounter_id",
        table_name="clinical_documents",
    )

    op.drop_index(
        "ix_clinical_documents_document_type",
        table_name="clinical_documents",
    )

    op.drop_index(
        "ix_clinical_documents_authored_by",
        table_name="clinical_documents",
    )

    op.drop_index(
        "ix_clinical_documents_amended_from_id",
        table_name="clinical_documents",
    )

    op.drop_table(
        "clinical_documents",
    )