"""
==============================================================================
LIGHTBURGH EMR

Diagnostic Service
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import ClinicalOrderStatus
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.clinical_results.enums import ClinicalResultStatus
from app.modules.diagnostics.enums import DiagnosticCategory
from app.modules.diagnostics.exceptions import (
    DiagnosticCategoryMismatchError,
    DiagnosticInvestigationNotFoundError,
    DiagnosticReportAlreadyExistsError,
    DiagnosticReportFinalizedError,
    DiagnosticReportNotFoundError,
    DiagnosticReportOrderNotFoundError,
    DiagnosticReportOrderNotInProgressError,
    DiagnosticReportOrderCancelledError,
    DiagnosticReportStaffNotFoundError,
    DiagnosticReportStaffHospitalMismatchError,
)
from app.modules.diagnostics.models import (
    DiagnosticInvestigation,
    DiagnosticReport,
    DiagnosticReportAttachment,
)
from app.modules.diagnostics.repositories import (
    DiagnosticRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.episode.services.episode_clinical_workflow_service import (
    EpisodeClinicalWorkflowService,
)
from app.modules.staff.repository import StaffRepository
from app.storage import LocalStorage


class DiagnosticService:
    """
    Business logic for diagnostic investigations and reports.
    """

    def __init__(
        self,
        *,
        repository: DiagnosticRepository,
        clinical_order_repository: ClinicalOrderRepository,
        episode_repository: EpisodeRepository,
        staff_repository: StaffRepository,
        event_service: ClinicalEventService,
        storage: LocalStorage,
        episode_clinical_workflow_service: EpisodeClinicalWorkflowService,
    ) -> None:
        self.repository = repository
        self.clinical_order_repository = clinical_order_repository
        self.episode_repository = episode_repository
        self.staff_repository = staff_repository
        self.event_service = event_service
        self.storage = storage
        self.episode_clinical_workflow_service = (
            episode_clinical_workflow_service
        )

    def list_investigations(
        self,
        *,
        hospital_id,
    ) -> list[DiagnosticInvestigation]:
        return self.repository.list_active_investigations(
            hospital_id=hospital_id,
        )

    def get_investigation(
        self,
        *,
        hospital_id,
        investigation_id: UUID,
    ) -> DiagnosticInvestigation:
        investigation = self.repository.get_investigation(
            hospital_id=hospital_id,
            investigation_id=investigation_id,
        )

        if investigation is None:
            raise DiagnosticInvestigationNotFoundError(
                "Diagnostic investigation not found.",
            )

        return investigation

    def _resolve_report_investigation(
        self,
        *,
        context: RequestContext,
        order,
        investigation_id: UUID,
    ) -> DiagnosticInvestigation:
        """
        Resolve the investigation used by a diagnostic report.

        Structured DIAGNOSTIC orders provide an explicit investigation ID.
        Legacy RADIOLOGY orders may only contain a study_code in their
        details payload. Legacy aliases are resolved here so the frontend
        does not need to understand historical order formats.
        """

        investigation = self.get_investigation(
            hospital_id=context.hospital_id,
            investigation_id=investigation_id,
        )

        if order.order_type.value != "RADIOLOGY":
            return investigation

        if investigation.category != DiagnosticCategory.RADIOLOGY:
            raise DiagnosticCategoryMismatchError(
                "Radiology reports must reference a RADIOLOGY investigation.",
            )

        return investigation

    def _resolve_legacy_radiology_investigation(
        self,
        *,
        context: RequestContext,
        order,
    ) -> DiagnosticInvestigation:
        """
        Resolve a legacy RADIOLOGY order to the hospital catalogue.

        Legacy radiology orders predate ClinicalOrderItem support and store
        the requested study as details.study_code. CXR is the historical
        alias for the current XRAY catalogue investigation.
        """

        details = order.details or {}
        study_code = details.get("study_code")

        if not isinstance(study_code, str) or not study_code.strip():
            raise DiagnosticInvestigationNotFoundError(
                "Legacy radiology order does not specify a study code.",
            )

        normalized_code = study_code.strip().upper()

        legacy_aliases = {
            "CXR": "XRAY",
        }

        catalogue_code = legacy_aliases.get(
            normalized_code,
            normalized_code,
        )

        investigation = self.repository.get_investigation_by_code(
            hospital_id=context.hospital_id,
            code=catalogue_code,
        )

        if investigation is None or not investigation.active:
            raise DiagnosticInvestigationNotFoundError(
                f"Radiology investigation '{catalogue_code}' "
                "is not available in the hospital catalogue.",
            )

        if investigation.category != DiagnosticCategory.RADIOLOGY:
            raise DiagnosticCategoryMismatchError(
                "Legacy radiology study does not resolve to a "
                "RADIOLOGY investigation.",
            )

        return investigation

    def create_investigation(
        self,
        *,
        hospital_id,
        code: str,
        name: str,
        category: DiagnosticCategory,
        description: str | None,
        report_template: dict,
    ) -> DiagnosticInvestigation:
        normalized_code = code.strip().upper()
        normalized_name = name.strip()

        if not normalized_code:
            raise ValueError(
                "Diagnostic investigation code is required.",
            )

        if not normalized_name:
            raise ValueError(
                "Diagnostic investigation name is required.",
            )

        existing = self.repository.get_investigation_by_code(
            hospital_id=hospital_id,
            code=normalized_code,
        )

        if existing is not None:
            raise ValueError(
                f"Diagnostic investigation '{normalized_code}' "
                "already exists.",
            )

        investigation = DiagnosticInvestigation(
            hospital_id=hospital_id,
            code=normalized_code,
            name=normalized_name,
            category=category,
            description=(
                description.strip()
                if description
                else None
            ),
            report_template=report_template,
            active=True,
        )

        self.repository.create_investigation(
            investigation=investigation,
        )

        self.repository.save()

        created = self.repository.get_investigation_by_code(
            hospital_id=hospital_id,
            code=normalized_code,
        )

        if created is None:
            raise RuntimeError(
                "Diagnostic investigation could not be "
                "reloaded after creation.",
            )

        return created

    def create_report(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
        investigation_id: UUID | None,
        category: DiagnosticCategory,
        findings: str | None,
        impression: str | None,
        interpretation: str | None,
        recommendations: str | None,
        measurements: dict | None,
    ) -> DiagnosticReport:
        order = self._get_order(
            context=context,
            order_id=order_id,
        )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise DiagnosticReportOrderCancelledError(
                "Diagnostic report cannot be created for a cancelled order.",
            )

        if order.status == ClinicalOrderStatus.COMPLETED:
            raise DiagnosticReportAlreadyExistsError(
                "A diagnostic report cannot be created for a completed order.",
            )

        if order.status != ClinicalOrderStatus.IN_PROGRESS:
            raise DiagnosticReportOrderNotInProgressError(
                "Clinical Order must be in progress before "
                "a diagnostic report can be created.",
            )

        if order.order_type.value not in (
            "DIAGNOSTIC",
            "RADIOLOGY",
        ):
            raise ValueError(
                "Diagnostic reports require a DIAGNOSTIC or "
                "RADIOLOGY clinical order.",
            )

        existing = self.repository.get_report_by_order(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

        if existing is not None:
            raise DiagnosticReportAlreadyExistsError(
                "A diagnostic report already exists "
                "for this clinical order.",
            )

        if order.order_type.value == "RADIOLOGY":
            investigation = (
                self._resolve_legacy_radiology_investigation(
                    context=context,
                    order=order,
                )
            )
        else:
            if investigation_id is None:
                raise DiagnosticInvestigationNotFoundError(
                    "Diagnostic investigation is required for "
                    "DIAGNOSTIC clinical orders.",
                )

            investigation = self._resolve_report_investigation(
                context=context,
                order=order,
                investigation_id=investigation_id,
            )

        if investigation.category != category:
            raise DiagnosticCategoryMismatchError(
                "Diagnostic report category does not match "
                "the investigation category.",
            )

        report = DiagnosticReport(
            order_id=order.id,
            investigation_id=investigation.id,
            category=category,
            status=ClinicalResultStatus.DRAFT,
            findings=findings,
            impression=impression,
            interpretation=interpretation,
            recommendations=recommendations,
            measurements=measurements,
        )

        self.repository.create_report(
            report=report,
        )

        self.repository.save()

        created = self.repository.get_report(
            hospital_id=context.hospital_id,
            report_id=report.id,
        )

        if created is None:
            raise RuntimeError(
                "Diagnostic report could not be reloaded "
                "after creation.",
            )

        return created

    def get_report_by_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> DiagnosticReport:
        report = self.repository.get_report_by_order(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

        if report is None:
            raise DiagnosticReportNotFoundError(
                "Diagnostic report not found.",
            )

        return report


    def get_report(
        self,
        *,
        context: RequestContext,
        report_id: UUID,
    ) -> DiagnosticReport:
        report = self.repository.get_report(
            hospital_id=context.hospital_id,
            report_id=report_id,
        )

        if report is None:
            raise DiagnosticReportNotFoundError(
                "Diagnostic report not found.",
            )

        return report

    def update_report(
        self,
        *,
        context: RequestContext,
        report_id: UUID,
        findings: str | None,
        impression: str | None,
        interpretation: str | None,
        recommendations: str | None,
        measurements: dict | None,
    ) -> DiagnosticReport:
        report = self.get_report(
            context=context,
            report_id=report_id,
        )

        if report.status == ClinicalResultStatus.FINAL:
            raise DiagnosticReportFinalizedError(
                "A finalized diagnostic report cannot be edited.",
            )

        report.findings = findings
        report.impression = impression
        report.interpretation = interpretation
        report.recommendations = recommendations
        report.measurements = measurements

        self.repository.save()

        self.repository.refresh(report)

        return report

    def finalize_report(
        self,
        *,
        context: RequestContext,
        report_id: UUID,
    ) -> DiagnosticReport:
        report = self.get_report(
            context=context,
            report_id=report_id,
        )

        if report.status == ClinicalResultStatus.FINAL:
            raise DiagnosticReportFinalizedError(
                "Diagnostic report has already been finalized.",
            )

        order = self._get_order(
            context=context,
            order_id=report.order_id,
        )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise DiagnosticReportOrderCancelledError(
                "Cancelled Clinical Orders cannot be finalized.",
            )

        if order.status != ClinicalOrderStatus.IN_PROGRESS:
            raise DiagnosticReportOrderNotInProgressError(
                "Clinical Order must be in progress before "
                "its diagnostic report can be finalized.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        finalized_at = datetime.now(UTC)

        try:
            report.status = ClinicalResultStatus.FINAL
            report.reported_at = finalized_at
            report.recorded_by = staff.id
            report.recorded_at = finalized_at

            order.status = ClinicalOrderStatus.COMPLETED
            order.completed_at = finalized_at

            self.event_service.create_event(
                context=context,
                encounter_id=order.encounter_id,
                event_type=EventType.RESULT_RECORDED,
                performed_by=staff.id,
                occurred_at=finalized_at,
                payload={
                    "clinical_order_id": str(order.id),
                    "diagnostic_report_id": str(report.id),
                    "category": (
                        report.category.value
                        if hasattr(report.category, "value")
                        else report.category
                    ),
                    "status": ClinicalResultStatus.FINAL.value,
                },
                commit=False,
            )

            episode = self.episode_repository.get_by_id(
                hospital_id=context.hospital_id,
                episode_id=order.encounter.episode_id,
            )

            if episode is None:
                raise RuntimeError(
                    "Episode could not be loaded for diagnostic "
                    "workflow finalization.",
                )

            self.episode_clinical_workflow_service.queue_doctor_review_if_ready(
                context=context,
                episode=episode,
            )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        created = self.repository.get_report(
            hospital_id=context.hospital_id,
            report_id=report.id,
        )

        if created is None:
            raise RuntimeError(
                "Diagnostic report could not be reloaded "
                "after finalization.",
            )

        return created

    def list_attachments(
        self,
        *,
        context: RequestContext,
        report_id: UUID,
    ) -> list[DiagnosticReportAttachment]:
        self.get_report(
            context=context,
            report_id=report_id,
        )

        return self.repository.list_attachments(
            report_id=report_id,
        )


    def get_attachment_content(
        self,
        *,
        context: RequestContext,
        attachment_id: UUID,
    ) -> tuple[DiagnosticReportAttachment, bytes]:
        attachment = self.repository.get_attachment(
            attachment_id=attachment_id,
        )

        if attachment is None:
            raise DiagnosticReportNotFoundError(
                "Diagnostic report attachment not found.",
            )

        self.get_report(
            context=context,
            report_id=attachment.report_id,
        )

        return (
            attachment,
            self.storage.read(
                storage_key=attachment.storage_key,
            ),
        )


    def create_attachment(
        self,
        *,
        context: RequestContext,
        report_id: UUID,
        file_name: str,
        content_type: str,
        content: bytes,
        description: str | None,
    ) -> DiagnosticReportAttachment:
        report = self.get_report(
            context=context,
            report_id=report_id,
        )

        if report.status == ClinicalResultStatus.FINAL:
            raise DiagnosticReportFinalizedError(
                "Attachments cannot be added to a finalized "
                "diagnostic report.",
            )

        storage_key = self.storage.save(
            content=content,
            original_filename=file_name,
            prefix="diagnostics",
        )

        attachment = DiagnosticReportAttachment(
            report_id=report.id,
            file_name=file_name,
            content_type=content_type,
            storage_key=storage_key,
            description=description,
        )

        self.repository.create_attachment(
            attachment=attachment,
        )

        self.repository.save()

        self.repository.refresh(attachment)

        return attachment

    def _get_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ):
        order = self.clinical_order_repository.get_by_id(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

        if order is None:
            raise DiagnosticReportOrderNotFoundError(
                "Clinical Order not found.",
            )

        return order

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        staff = self.staff_repository.get_by_user_account_id(
            context.hospital_id,
            context.user_id,
        )

        if staff is None:
            raise DiagnosticReportStaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise DiagnosticReportStaffHospitalMismatchError(
                "Authenticated Staff does not belong to this Hospital.",
            )

        return staff
