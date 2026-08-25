from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.terminology.enums import TerminologySystem


class TerminologyConceptResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    system: TerminologySystem
    code: str
    display_name: str
    description: str | None
    active: bool
