"""
==============================================================================
LIGHTBURGH EMR

Clinical Result Service
==============================================================================
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.context import RequestContext
from app.modules.clinical_orders.enums import (
    ClinicalOrderStatus,
    ClinicalOrderType,
)
from app.modules.clinical_orders.models import ClinicalOrder
from app.modules.clinical_orders.repositories import (
    ClinicalOrderRepository,
)
from app.modules.clinical_results.enums import (
    ClinicalResultStatus,
    ClinicalResultType,
)
from app.modules.clinical_results.exceptions import (
    ClinicalResultDuplicateAnalyteError,
    ClinicalResultInvalidValueError,
    ClinicalResultLaboratoryTestNotFoundError,
    ClinicalResultMissingRequiredAnalyteError,
    ClinicalResultAlreadyFinalError,
    ClinicalResultNotFoundError,
    ClinicalResultOrderAlreadyCompletedError,
    ClinicalResultOrderCancelledError,
    ClinicalResultOrderNotInProgressError,
    ClinicalResultOrderNotFoundError,
    ClinicalResultStaffHospitalMismatchError,
    ClinicalResultStaffNotFoundError,
    ClinicalResultUnknownAnalyteError,
    ClinicalResultUnsupportedOrderTypeError,
)
from app.modules.clinical_results.models import (
    ClinicalResult,
    ClinicalResultValue,
)
from app.modules.clinical_results.repositories import (
    ClinicalResultRepository,
)
from app.modules.episode.models import (
    EpisodeFlowStatus,
)
from app.modules.episode.repositories.episode_repository import (
    EpisodeRepository,
)
from app.modules.laboratory.enums import (
    LaboratoryAnalyteDataType,
)
from app.modules.laboratory.repositories import (
    LaboratoryTestRepository,
)
from app.modules.events.enums import EventType
from app.modules.events.services.event_service import (
    ClinicalEventService,
)
from app.modules.staff.repository import StaffRepository


class ClinicalResultService:
    """
    Business logic for Clinical Results.
    """

    def __init__(
        self,
        *,
        repository: ClinicalResultRepository,
        clinical_order_repository: ClinicalOrderRepository,
        episode_repository: EpisodeRepository,
        laboratory_test_repository: LaboratoryTestRepository,
        event_service: ClinicalEventService,
        staff_repository: StaffRepository,
    ) -> None:
        self.repository = repository
        self.clinical_order_repository = (
            clinical_order_repository
        )
        self.episode_repository = episode_repository
        self.laboratory_test_repository = laboratory_test_repository
        self.event_service = event_service
        self.staff_repository = staff_repository

    def _get_authenticated_staff(
        self,
        *,
        context: RequestContext,
    ):
        staff = self.staff_repository.get_by_user_account_id(
            hospital_id=context.hospital_id,
            user_account_id=context.user_id,
        )

        if staff is None:
            raise ClinicalResultStaffNotFoundError(
                "Authenticated user does not have a Staff profile.",
            )

        if staff.hospital_id != context.hospital_id:
            raise ClinicalResultStaffHospitalMismatchError(
                "Staff member does not belong to the authenticated Hospital.",
            )

        return staff

    def _get_episode_for_order(
        self,
        *,
        context: RequestContext,
        order: ClinicalOrder,
    ):
        episode = self.episode_repository.get_by_id(
            hospital_id=context.hospital_id,
            episode_id=order.encounter.episode_id,
        )

        if episode is None:
            raise ClinicalResultOrderNotFoundError(
                "Episode for Clinical Order not found.",
            )

        return episode

    def _get_order(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> ClinicalOrder:
        order = self.clinical_order_repository.get_by_id(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

        if order is None:
            raise ClinicalResultOrderNotFoundError(
                "Clinical Order not found.",
            )

        return order

    def _get_laboratory_test_for_order(
        self,
        *,
        context: RequestContext,
        order: ClinicalOrder,
    ):
        details = order.details or {}

        test_code = details.get("test_code")

        if not isinstance(test_code, str) or not test_code.strip():
            raise ClinicalResultLaboratoryTestNotFoundError(
                "Laboratory Order does not reference a laboratory test code.",
            )

        test = self.laboratory_test_repository.get_by_code(
            hospital_id=context.hospital_id,
            code=test_code.strip(),
        )

        if test is None:
            raise ClinicalResultLaboratoryTestNotFoundError(
                f"Laboratory test '{test_code}' not found.",
            )

        return test

    @staticmethod
    def _validate_value_shape(
        *,
        analyte,
        value_numeric,
        value_text,
        value_boolean,
        value_code,
    ) -> None:
        provided = [
            value_numeric is not None,
            value_text is not None,
            value_boolean is not None,
            value_code is not None,
        ]

        if sum(provided) != 1:
            raise ClinicalResultInvalidValueError(
                f"Exactly one value is required for analyte '{analyte.code}'.",
            )

        expected = analyte.data_type

        if expected == LaboratoryAnalyteDataType.NUMERIC:
            if value_numeric is None:
                raise ClinicalResultInvalidValueError(
                    f"Analyte '{analyte.code}' requires a numeric value.",
                )
            return

        if expected == LaboratoryAnalyteDataType.TEXT:
            if value_text is None:
                raise ClinicalResultInvalidValueError(
                    f"Analyte '{analyte.code}' requires a text value.",
                )
            return

        if expected == LaboratoryAnalyteDataType.BOOLEAN:
            if value_boolean is None:
                raise ClinicalResultInvalidValueError(
                    f"Analyte '{analyte.code}' requires a boolean value.",
                )
            return

        if expected == LaboratoryAnalyteDataType.CODED:
            if value_code is None:
                raise ClinicalResultInvalidValueError(
                    f"Analyte '{analyte.code}' requires a coded value.",
                )

            options = analyte.options or []

            if options and value_code not in options:
                raise ClinicalResultInvalidValueError(
                    f"Invalid value '{value_code}' for analyte "
                    f"'{analyte.code}'.",
                )
            return

        raise ClinicalResultInvalidValueError(
            f"Unsupported datatype for analyte '{analyte.code}'.",
        )

    @staticmethod
    def _calculate_abnormal_flag(
        *,
        analyte,
        value_numeric,
        supplied_flag=None,
    ) -> str | None:
        """
        Derive an abnormal flag from the configured numeric
        reference interval unless the caller supplied one.
        """

        if supplied_flag:
            return supplied_flag

        if value_numeric is None:
            return None

        if (
            analyte.reference_low is not None
            and value_numeric < float(
                analyte.reference_low,
            )
        ):
            return "LOW"

        if (
            analyte.reference_high is not None
            and value_numeric > float(
                analyte.reference_high,
            )
        ):
            return "HIGH"

        return None


    def _build_structured_result_values(
        self,
        *,
        laboratory_test,
        values,
        legacy_result_data,
        require_all_required: bool = True,
    ) -> list[dict]:
        analytes_by_id = {
            analyte.id: analyte
            for analyte in laboratory_test.analytes
        }

        analytes_by_code = {
            analyte.code: analyte
            for analyte in laboratory_test.analytes
        }

        normalized_values = []

        if values:
            seen_analytes = set()

            for value in values:
                if isinstance(value, dict):
                    get_value = value.get
                else:
                    get_value = lambda key: getattr(
                        value,
                        key,
                        None,
                    )

                analyte_id = get_value("analyte_id")

                analyte = analytes_by_id.get(analyte_id)

                if analyte is None:
                    raise ClinicalResultUnknownAnalyteError(
                        f"Analyte '{analyte_id}' does not belong "
                        f"to laboratory test '{laboratory_test.code}'.",
                    )

                if analyte.id in seen_analytes:
                    raise ClinicalResultDuplicateAnalyteError(
                        f"Analyte '{analyte.code}' was submitted more than once.",
                    )

                seen_analytes.add(analyte.id)

                value_numeric = get_value("value_numeric")
                value_text = get_value("value_text")
                value_boolean = get_value("value_boolean")
                value_code = get_value("value_code")
                abnormal_flag = get_value("abnormal_flag")
                comment = get_value("comment")

                self._validate_value_shape(
                    analyte=analyte,
                    value_numeric=value_numeric,
                    value_text=value_text,
                    value_boolean=value_boolean,
                    value_code=value_code,
                )

                abnormal_flag = (
                    self._calculate_abnormal_flag(
                        analyte=analyte,
                        value_numeric=value_numeric,
                        supplied_flag=abnormal_flag,
                    )
                )

                normalized_values.append(
                    {
                        "analyte": analyte,
                        "value_numeric": value_numeric,
                        "value_text": value_text,
                        "value_boolean": value_boolean,
                        "value_code": value_code,
                        "abnormal_flag": abnormal_flag,
                        "comment": comment,
                    }
                )

        elif legacy_result_data:
            for code, raw_value in legacy_result_data.items():
                # Legacy clients historically embedded report-level
                # metadata inside result_data. Keep that payload
                # compatible without treating metadata as an analyte.
                if str(code) in {
                    "interpretation",
                    "specimen",
                    "collected_at",
                    "reported_at",
                }:
                    continue

                analyte = analytes_by_code.get(str(code))

                if analyte is None:
                    raise ClinicalResultUnknownAnalyteError(
                        f"Unknown analyte '{code}' for "
                        f"laboratory test '{laboratory_test.code}'.",
                    )

                value_numeric = None
                value_text = None
                value_boolean = None
                value_code = None

                if analyte.data_type == LaboratoryAnalyteDataType.NUMERIC:
                    try:
                        value_numeric = float(raw_value)
                    except (TypeError, ValueError) as exc:
                        raise ClinicalResultInvalidValueError(
                            f"Invalid numeric value for analyte "
                            f"'{analyte.code}'.",
                        ) from exc

                elif analyte.data_type == LaboratoryAnalyteDataType.BOOLEAN:
                    if not isinstance(raw_value, bool):
                        raise ClinicalResultInvalidValueError(
                            f"Invalid boolean value for analyte "
                            f"'{analyte.code}'.",
                        )
                    value_boolean = raw_value

                elif analyte.data_type == LaboratoryAnalyteDataType.CODED:
                    value_code = str(raw_value)

                else:
                    value_text = str(raw_value)

                self._validate_value_shape(
                    analyte=analyte,
                    value_numeric=value_numeric,
                    value_text=value_text,
                    value_boolean=value_boolean,
                    value_code=value_code,
                )

                abnormal_flag = (
                    self._calculate_abnormal_flag(
                        analyte=analyte,
                        value_numeric=value_numeric,
                    )
                )

                normalized_values.append(
                    {
                        "analyte": analyte,
                        "value_numeric": value_numeric,
                        "value_text": value_text,
                        "value_boolean": value_boolean,
                        "value_code": value_code,
                        "abnormal_flag": abnormal_flag,
                        "comment": None,
                    }
                )

        submitted_ids = {
            item["analyte"].id
            for item in normalized_values
        }

        missing_required = [
            analyte.code
            for analyte in laboratory_test.analytes
            if analyte.required
            and analyte.id not in submitted_ids
        ]

        if require_all_required and missing_required:
            raise ClinicalResultMissingRequiredAnalyteError(
                "Missing required analyte(s): "
                + ", ".join(missing_required),
            )

        return normalized_values

    def record_result(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
        result_type: ClinicalResultType,
        status: ClinicalResultStatus = ClinicalResultStatus.FINAL,
        result_data: dict | None = None,
        values=None,
        specimen: str | None = None,
        collected_at=None,
        reported_at=None,
        interpretation: str | None = None,
    ) -> ClinicalResult:
        """
        Record a clinical result and complete the underlying order.

        Laboratory results are validated against the configured laboratory
        test analytes and persisted as structured ClinicalResultValue rows.
        Legacy result_data remains temporarily supported.
        """

        order = self._get_order(
            context=context,
            order_id=order_id,
        )

        if order.order_type not in (
            ClinicalOrderType.LABORATORY,
            ClinicalOrderType.RADIOLOGY,
        ):
            raise ClinicalResultUnsupportedOrderTypeError(
                "Results can only be recorded for laboratory "
                "or radiology orders.",
            )

        expected_result_type = {
            ClinicalOrderType.LABORATORY:
                ClinicalResultType.LABORATORY,
            ClinicalOrderType.RADIOLOGY:
                ClinicalResultType.RADIOLOGY,
        }[order.order_type]

        if result_type != expected_result_type:
            raise ClinicalResultUnsupportedOrderTypeError(
                "Result type does not match the Clinical Order type.",
            )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise ClinicalResultOrderCancelledError(
                "Cancelled Clinical Orders cannot receive results.",
            )

        if order.status == ClinicalOrderStatus.COMPLETED:
            raise ClinicalResultOrderAlreadyCompletedError(
                "Clinical Order is already completed.",
            )

        if (
            status == ClinicalResultStatus.DRAFT
            and order.status != ClinicalOrderStatus.IN_PROGRESS
        ):
            raise ClinicalResultOrderNotInProgressError(
                "A draft result can only be recorded while "
                "the Clinical Order is in progress.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        recorded_at = datetime.now(UTC)

        structured_values = []

        if order.order_type == ClinicalOrderType.LABORATORY:
            laboratory_test = self._get_laboratory_test_for_order(
                context=context,
                order=order,
            )

            structured_values = self._build_structured_result_values(
                laboratory_test=laboratory_test,
                values=values,
                legacy_result_data=result_data,
                require_all_required=(
                    status == ClinicalResultStatus.FINAL
                ),
            )

            if specimen is None:
                specimen = laboratory_test.specimen

        legacy_interpretation = None

        if result_data:
            raw_interpretation = result_data.get("interpretation")
            if isinstance(raw_interpretation, str):
                legacy_interpretation = raw_interpretation

        result = ClinicalResult(
            order_id=order.id,
            result_type=result_type,
            status=status,
            result_data=result_data or {},
            specimen=specimen,
            collected_at=collected_at,
            reported_at=reported_at or recorded_at,
            interpretation=(
                interpretation
                if interpretation is not None
                else legacy_interpretation
            ),
            recorded_by=staff.id,
            recorded_at=recorded_at,
        )

        for item in structured_values:
            result.values.append(
                ClinicalResultValue(
                    analyte_id=item["analyte"].id,
                    value_numeric=item["value_numeric"],
                    value_text=item["value_text"],
                    value_boolean=item["value_boolean"],
                    value_code=item["value_code"],
                    abnormal_flag=item["abnormal_flag"],
                    comment=item["comment"],
                )
            )

        episode = self._get_episode_for_order(
            context=context,
            order=order,
        )

        try:
            self.repository.create(
                result=result,
            )

            self.repository.db.flush()

            if status == ClinicalResultStatus.FINAL:
                order.status = ClinicalOrderStatus.COMPLETED
                order.completed_at = recorded_at

            self.event_service.create_event(
                context=context,
                encounter_id=order.encounter_id,
                event_type=EventType.RESULT_RECORDED,
                performed_by=staff.id,
                occurred_at=recorded_at,
                payload={
                    "clinical_order_id": str(order.id),
                    "clinical_result_id": str(result.id),
                    "result_type": result_type.value,
                },
                commit=False,
            )

            if status == ClinicalResultStatus.FINAL:
                outstanding_orders = (
                    self.clinical_order_repository
                    .list_outstanding_investigation_orders_for_episode(
                        hospital_id=context.hospital_id,
                        episode_id=episode.id,
                    )
                )

                if (
                    episode.flow_status
                    == EpisodeFlowStatus.AWAITING_INVESTIGATIONS
                    and not outstanding_orders
                ):
                    episode.flow_status = (
                        EpisodeFlowStatus.AWAITING_REVIEW
                    )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(
            result,
        )

        return result

    def update_draft_result(
        self,
        *,
        context: RequestContext,
        result_id: UUID,
        result_data: dict | None = None,
        values=None,
        specimen: str | None = None,
        collected_at=None,
        reported_at=None,
        interpretation: str | None = None,
    ) -> ClinicalResult:
        """
        Update an existing draft laboratory result.
        """

        result = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            result_id=result_id,
        )

        if result is None:
            raise ClinicalResultNotFoundError(
                "Clinical Result not found.",
            )

        if result.status == ClinicalResultStatus.FINAL:
            raise ClinicalResultAlreadyFinalError(
                "Finalized Clinical Results cannot be edited.",
            )

        order = self._get_order(
            context=context,
            order_id=result.order_id,
        )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise ClinicalResultOrderCancelledError(
                "Cancelled Clinical Orders cannot be edited.",
            )

        if order.status != ClinicalOrderStatus.IN_PROGRESS:
            raise ClinicalResultOrderNotInProgressError(
                "A draft result can only be edited while "
                "the Clinical Order is in progress.",
            )

        laboratory_test = None

        if result.result_type == ClinicalResultType.LABORATORY:
            laboratory_test = self._get_laboratory_test_for_order(
                context=context,
                order=order,
            )

            structured_values = self._build_structured_result_values(
                laboratory_test=laboratory_test,
                values=values,
                legacy_result_data=result_data,
                require_all_required=False,
            )

            if specimen is None:
                specimen = laboratory_test.specimen

        legacy_interpretation = None

        if result_data:
            raw_interpretation = result_data.get("interpretation")
            if isinstance(raw_interpretation, str):
                legacy_interpretation = raw_interpretation

        result.result_data = result_data or {}
        result.specimen = specimen
        result.collected_at = collected_at
        result.reported_at = reported_at
        result.interpretation = (
            interpretation
            if interpretation is not None
            else legacy_interpretation
        )

        self.repository.delete_values(
            result=result,
        )

        for item in structured_values:
            result.values.append(
                ClinicalResultValue(
                    analyte_id=item["analyte"].id,
                    value_numeric=item["value_numeric"],
                    value_text=item["value_text"],
                    value_boolean=item["value_boolean"],
                    value_code=item["value_code"],
                    abnormal_flag=item["abnormal_flag"],
                    comment=item["comment"],
                )
            )

        self.repository.db.commit()

        self.repository.refresh(result)

        return result


    def finalize_result(
        self,
        *,
        context: RequestContext,
        result_id: UUID,
    ) -> ClinicalResult:
        """
        Finalize a draft Clinical Result and complete its order.
        """

        result = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            result_id=result_id,
        )

        if result is None:
            raise ClinicalResultNotFoundError(
                "Clinical Result not found.",
            )

        if result.status == ClinicalResultStatus.FINAL:
            raise ClinicalResultAlreadyFinalError(
                "Clinical Result is already finalized.",
            )

        order = self._get_order(
            context=context,
            order_id=result.order_id,
        )

        if order.status == ClinicalOrderStatus.CANCELLED:
            raise ClinicalResultOrderCancelledError(
                "Cancelled Clinical Orders cannot be finalized.",
            )

        if order.status != ClinicalOrderStatus.IN_PROGRESS:
            raise ClinicalResultOrderNotInProgressError(
                "Clinical Order must be in progress before "
                "its result can be finalized.",
            )

        staff = self._get_authenticated_staff(
            context=context,
        )

        episode = self._get_episode_for_order(
            context=context,
            order=order,
        )

        finalized_at = datetime.now(UTC)

        try:
            result.status = ClinicalResultStatus.FINAL
            result.reported_at = (
                result.reported_at or finalized_at
            )

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
                    "clinical_result_id": str(result.id),
                    "result_type": result.result_type.value,
                    "status": ClinicalResultStatus.FINAL.value,
                },
                commit=False,
            )

            outstanding_orders = (
                self.clinical_order_repository
                .list_outstanding_investigation_orders_for_episode(
                    hospital_id=context.hospital_id,
                    episode_id=episode.id,
                )
            )

            if (
                episode.flow_status
                == EpisodeFlowStatus.AWAITING_INVESTIGATIONS
                and not outstanding_orders
            ):
                episode.flow_status = (
                    EpisodeFlowStatus.AWAITING_REVIEW
                )

            self.repository.db.commit()

        except Exception:
            self.repository.db.rollback()
            raise

        self.repository.refresh(result)

        return result


    def list_order_results(
        self,
        *,
        context: RequestContext,
        order_id: UUID,
    ) -> list[ClinicalResult]:
        self._get_order(
            context=context,
            order_id=order_id,
        )

        return self.repository.list_by_order(
            hospital_id=context.hospital_id,
            order_id=order_id,
        )

    def get_result(
        self,
        *,
        context: RequestContext,
        result_id: UUID,
    ) -> ClinicalResult:
        result = self.repository.get_by_id(
            hospital_id=context.hospital_id,
            result_id=result_id,
        )

        if result is None:
            raise ClinicalResultOrderNotFoundError(
                "Clinical Result not found.",
            )

        return result
