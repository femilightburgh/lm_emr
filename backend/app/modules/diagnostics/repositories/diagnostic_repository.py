"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Repository
==============================================================================
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.diagnostics.models import (
    DiagnosticInvestigation,
    DiagnosticReport,
    DiagnosticReportAttachment,
)


class DiagnosticRepository:
    """
    Persistence operations for diagnostic investigations and reports.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def list_active_investigations(
        self,
        *,
        hospital_id,
    ) -> list[DiagnosticInvestigation]:
        statement = (
            select(DiagnosticInvestigation)
            .where(
                DiagnosticInvestigation.hospital_id
                == hospital_id,
                DiagnosticInvestigation.active.is_(True),
            )
            .order_by(
                DiagnosticInvestigation.name.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    def get_investigation_by_code(
        self,
        *,
        hospital_id,
        code: str,
    ) -> DiagnosticInvestigation | None:
        statement = (
            select(DiagnosticInvestigation)
            .where(
                DiagnosticInvestigation.hospital_id
                == hospital_id,
                DiagnosticInvestigation.code == code,
            )
        )

        return self.db.scalar(statement)

    def get_investigation(
        self,
        *,
        hospital_id,
        investigation_id: UUID,
    ) -> DiagnosticInvestigation | None:
        statement = (
            select(DiagnosticInvestigation)
            .where(
                DiagnosticInvestigation.hospital_id
                == hospital_id,
                DiagnosticInvestigation.id
                == investigation_id,
            )
        )

        return self.db.scalar(statement)

    def get_report_by_order(
        self,
        *,
        hospital_id,
        order_id: UUID,
    ) -> DiagnosticReport | None:
        statement = (
            select(DiagnosticReport)
            .join(
                DiagnosticInvestigation,
                DiagnosticReport.investigation_id
                == DiagnosticInvestigation.id,
            )
            .options(
                selectinload(
                    DiagnosticReport.investigation,
                ),
                selectinload(
                    DiagnosticReport.attachments,
                ),
            )
            .where(
                DiagnosticReport.order_id == order_id,
                DiagnosticInvestigation.hospital_id
                == hospital_id,
            )
        )

        return self.db.scalar(statement)

    def get_report(
        self,
        *,
        hospital_id,
        report_id: UUID,
    ) -> DiagnosticReport | None:
        statement = (
            select(DiagnosticReport)
            .join(
                DiagnosticInvestigation,
                DiagnosticReport.investigation_id
                == DiagnosticInvestigation.id,
            )
            .options(
                selectinload(
                    DiagnosticReport.investigation,
                ),
                selectinload(
                    DiagnosticReport.attachments,
                ),
            )
            .where(
                DiagnosticReport.id == report_id,
                DiagnosticInvestigation.hospital_id
                == hospital_id,
            )
        )

        return self.db.scalar(statement)

    def list_reports_by_hospital(
        self,
        *,
        hospital_id,
    ) -> list[DiagnosticReport]:
        statement = (
            select(DiagnosticReport)
            .join(
                DiagnosticInvestigation,
                DiagnosticReport.investigation_id
                == DiagnosticInvestigation.id,
            )
            .options(
                selectinload(
                    DiagnosticReport.investigation,
                ),
                selectinload(
                    DiagnosticReport.attachments,
                ),
            )
            .where(
                DiagnosticInvestigation.hospital_id
                == hospital_id,
            )
            .order_by(
                DiagnosticReport.created_at.desc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    def create_investigation(
        self,
        *,
        investigation: DiagnosticInvestigation,
    ) -> DiagnosticInvestigation:
        self.db.add(investigation)
        return investigation

    def list_attachments(
        self,
        *,
        report_id,
    ) -> list[DiagnosticReportAttachment]:
        statement = (
            select(DiagnosticReportAttachment)
            .where(
                DiagnosticReportAttachment.report_id == report_id,
            )
            .order_by(
                DiagnosticReportAttachment.created_at.asc(),
            )
        )

        return list(
            self.db.scalars(statement),
        )

    def create_report(
        self,
        *,
        report: DiagnosticReport,
    ) -> DiagnosticReport:
        self.db.add(report)
        return report

    def get_attachment(
        self,
        *,
        attachment_id,
    ) -> DiagnosticReportAttachment | None:
        statement = (
            select(DiagnosticReportAttachment)
            .where(
                DiagnosticReportAttachment.id == attachment_id,
            )
        )

        return self.db.scalar(statement)

    def create_attachment(
        self,
        *,
        attachment: DiagnosticReportAttachment,
    ) -> DiagnosticReportAttachment:
        self.db.add(attachment)
        return attachment

    def save(self) -> None:
        self.db.commit()

    def refresh(
        self,
        instance,
    ) -> None:
        self.db.refresh(instance)
