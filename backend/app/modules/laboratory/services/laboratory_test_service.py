"""
==============================================================================
LIGHTBURGH EMR

Laboratory Test Service
==============================================================================
"""

from app.modules.laboratory.models import (
    LaboratoryTest,
    LaboratoryTestAnalyte,
)
from app.modules.laboratory.enums import (
    LaboratoryAnalyteDataType,
)

from app.modules.laboratory.exceptions import (
    LaboratoryAnalyteNotFoundError,
    LaboratoryAnalyteTestMismatchError,
    LaboratoryReferenceRangeError,
    LaboratoryTestNotFoundError,
)
from app.modules.laboratory.repositories import (
    LaboratoryTestRepository,
)


class LaboratoryTestService:
    """
    Business logic for the Laboratory Test catalogue.
    """

    def __init__(
        self,
        *,
        repository: LaboratoryTestRepository,
    ) -> None:
        self.repository = repository

    def create_test(
        self,
        *,
        hospital_id,
        code: str,
        name: str,
        specimen: str | None,
        description: str | None,
        analytes: list[dict],
    ) -> LaboratoryTest:
        normalized_code = code.strip().upper()
        normalized_name = name.strip()

        if not normalized_code:
            raise ValueError(
                "Laboratory test code is required."
            )

        if not normalized_name:
            raise ValueError(
                "Laboratory test name is required."
            )

        existing = self.repository.get_by_code(
            hospital_id=hospital_id,
            code=normalized_code,
        )

        if existing is not None:
            raise ValueError(
                f"Laboratory test '{normalized_code}' "
                "already exists."
            )

        analyte_codes: set[str] = set()
        normalized_analytes: list[dict] = []

        for index, analyte in enumerate(analytes):
            analyte_code = str(
                analyte.get("code", "")
            ).strip().upper()

            analyte_name = str(
                analyte.get("name", "")
            ).strip()

            if not analyte_code:
                raise ValueError(
                    f"Analyte {index + 1}: code is required."
                )

            if not analyte_name:
                raise ValueError(
                    f"Analyte '{analyte_code}': "
                    "name is required."
                )

            if analyte_code in analyte_codes:
                raise ValueError(
                    f"Duplicate analyte code "
                    f"'{analyte_code}'."
                )

            analyte_codes.add(analyte_code)

            data_type = analyte.get(
                "data_type"
            )

            low = analyte.get(
                "reference_low"
            )

            high = analyte.get(
                "reference_high"
            )

            if (
                low is not None
                and high is not None
                and low > high
            ):
                raise ValueError(
                    f"Analyte '{analyte_code}': "
                    "reference_low cannot be greater "
                    "than reference_high."
                )

            if (
                data_type == LaboratoryAnalyteDataType.CODED
            ):
                options = analyte.get("options")

                if not options:
                    raise ValueError(
                        f"Analyte '{analyte_code}': "
                        "coded analytes require options."
                    )

            elif analyte.get("options"):
                raise ValueError(
                    f"Analyte '{analyte_code}': "
                    "options are only valid for "
                    "coded analytes."
                )

            normalized_analytes.append({
                **analyte,
                "code": analyte_code,
                "name": analyte_name,
                "display_order": analyte.get(
                    "display_order",
                    index,
                ),
            })

        laboratory_test = LaboratoryTest(
            hospital_id=hospital_id,
            code=normalized_code,
            name=normalized_name,
            specimen=(
                specimen.strip()
                if specimen
                else None
            ),
            description=(
                description.strip()
                if description
                else None
            ),
            active=True,
        )

        self.repository.create(
            laboratory_test=laboratory_test,
        )

        for analyte in normalized_analytes:
            self.repository.create_analyte(
                analyte=LaboratoryTestAnalyte(
                    laboratory_test=laboratory_test,
                    code=analyte["code"],
                    name=analyte["name"],
                    data_type=analyte["data_type"],
                    unit=analyte.get("unit"),
                    reference_low=analyte.get(
                        "reference_low"
                    ),
                    reference_high=analyte.get(
                        "reference_high"
                    ),
                    reference_text=analyte.get(
                        "reference_text"
                    ),
                    options=analyte.get(
                        "options"
                    ),
                    required=bool(
                        analyte.get(
                            "required",
                            False,
                        )
                    ),
                    display_order=analyte.get(
                        "display_order",
                        0,
                    ),
                )
            )

        self.repository.save()

        created = self.repository.get_by_code(
            hospital_id=hospital_id,
            code=normalized_code,
        )

        if created is None:
            raise RuntimeError(
                "Laboratory test could not be reloaded "
                "after creation."
            )

        return created


    def create_analyte(
        self,
        *,
        hospital_id,
        test_code: str,
        code: str,
        name: str,
        data_type: LaboratoryAnalyteDataType,
        unit: str | None,
        reference_low: float | None,
        reference_high: float | None,
        reference_text: str | None,
        options: list | None,
        required: bool,
        display_order: int,
    ) -> LaboratoryTestAnalyte:
        """
        Add an analyte to an existing laboratory test.
        """

        normalized_test_code = test_code.strip().upper()
        normalized_code = code.strip().upper()
        normalized_name = name.strip()

        test = self.repository.get_by_code(
            hospital_id=hospital_id,
            code=normalized_test_code,
        )

        if test is None:
            raise LaboratoryTestNotFoundError(
                f"Laboratory test '{normalized_test_code}' was not found.",
            )

        if not normalized_code:
            raise ValueError(
                "Analyte code is required.",
            )

        if not normalized_name:
            raise ValueError(
                "Analyte name is required.",
            )

        existing_codes = {
            analyte.code.upper()
            for analyte in test.analytes
        }

        if normalized_code in existing_codes:
            raise ValueError(
                f"Analyte '{normalized_code}' already exists "
                f"for laboratory test '{normalized_test_code}'.",
            )

        if (
            reference_low is not None
            and reference_high is not None
            and reference_low > reference_high
        ):
            raise LaboratoryReferenceRangeError(
                "reference_low cannot be greater than reference_high.",
            )

        if data_type == LaboratoryAnalyteDataType.CODED:
            if not options:
                raise ValueError(
                    f"Analyte '{normalized_code}': "
                    "coded analytes require options.",
                )
        elif options:
            raise ValueError(
                f"Analyte '{normalized_code}': "
                "options are only valid for coded analytes.",
            )

        analyte = LaboratoryTestAnalyte(
            laboratory_test_id=test.id,
            code=normalized_code,
            name=normalized_name,
            data_type=data_type,
            unit=unit.strip() if unit else None,
            reference_low=reference_low,
            reference_high=reference_high,
            reference_text=(
                reference_text.strip()
                if reference_text
                else None
            ),
            options=options,
            required=required,
            display_order=display_order,
        )

        self.repository.create_analyte(
            analyte=analyte,
        )

        self.repository.save()

        return analyte


    def update_analyte(
        self,
        *,
        hospital_id,
        test_code: str,
        analyte_id,
        updates: dict,
    ):
        test = self.repository.get_by_code(
            hospital_id=hospital_id,
            code=test_code,
        )

        if test is None:
            raise LaboratoryTestNotFoundError(
                f"Laboratory test '{test_code}' was not found.",
            )

        analyte = self.repository.get_analyte(
            hospital_id=hospital_id,
            test_code=test_code,
            analyte_id=analyte_id,
        )

        if analyte is None:
            raise LaboratoryAnalyteNotFoundError(
                f"Laboratory analyte '{analyte_id}' was not found.",
            )

        if analyte.laboratory_test_id != test.id:
            raise LaboratoryAnalyteTestMismatchError(
                "Laboratory analyte does not belong to the laboratory test.",
            )

        low = updates.get(
            "reference_low",
            analyte.reference_low,
        )

        high = updates.get(
            "reference_high",
            analyte.reference_high,
        )

        if (
            low is not None
            and high is not None
            and low > high
        ):
            raise LaboratoryReferenceRangeError(
                "reference_low cannot be greater than reference_high.",
            )

        for field, value in updates.items():
            setattr(
                analyte,
                field,
                value,
            )

        self.repository.save()

        return analyte


    def list_active_tests(
        self,
        *,
        hospital_id,
    ) -> list[LaboratoryTest]:
        return self.repository.list_active(
            hospital_id=hospital_id,
        )
