"""backfill staff employment history

Revision ID: b9e61eec6ff5
Revises: bee0289be087
Create Date: 2026-08-09

"""

from alembic import op
import sqlalchemy as sa
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = "b9e61eec6ff5"
down_revision = "bee0289be087"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create one StaffEmployment record for every existing Staff record.

    Existing employment information is copied without modification.
    """

    connection = op.get_bind()

    staff_rows = connection.execute(
        sa.text(
            """
            SELECT
                id,
                profession,
                employment_status,
                employment_type,
                date_employed,
                date_left
            FROM staff
            """
        )
    ).mappings().all()

    for staff in staff_rows:
        connection.execute(
            sa.text(
                """
                INSERT INTO staff_employments (
                    id,
                    staff_id,
                    profession,
                    employment_status,
                    employment_type,
                    date_employed,
                    date_left,
                    created_at,
                    updated_at
                )
                VALUES (
                    :id,
                    :staff_id,
                    :profession,
                    :employment_status,
                    :employment_type,
                    :date_employed,
                    :date_left,
                    NOW(),
                    NOW()
                )
                """
            ),
            {
                "id": str(uuid4()),
                "staff_id": str(staff["id"]),
                "profession": staff["profession"],
                "employment_status": staff["employment_status"],
                "employment_type": staff["employment_type"],
                "date_employed": staff["date_employed"],
                "date_left": staff["date_left"],
            },
        )


def downgrade() -> None:
    """
    Remove the employment records created by this backfill.

    The Staff records themselves are untouched.
    """

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM staff_employments
            """
        )
    )