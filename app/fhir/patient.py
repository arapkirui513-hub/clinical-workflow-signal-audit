from typing import Literal

from pydantic import BaseModel, Field


class FHIRPatient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: str = Field(min_length=1)
    active: bool = True
    gender: Literal["male", "female", "other", "unknown"] | None = None
    birthDate: str | None = None