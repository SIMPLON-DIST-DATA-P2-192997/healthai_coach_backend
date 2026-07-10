from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["Mild", "Moderate", "Severe"]


class MedicalProfileBase(BaseModel):
    disease_type: str | None = None
    severity: Severity | None = None
    cholesterol_mg_dl: float | None = Field(default=None, ge=0)
    blood_pressure_mmhg: float | None = Field(default=None, ge=0)
    glucose_mg_dl: float | None = Field(default=None, ge=0)
    recorded_at: datetime


class MedicalProfileCreate(MedicalProfileBase):
    pass


class MedicalProfileUpdate(BaseModel):
    disease_type: str | None = None
    severity: Severity | None = None
    cholesterol_mg_dl: float | None = Field(default=None, ge=0)
    blood_pressure_mmhg: float | None = Field(default=None, ge=0)
    glucose_mg_dl: float | None = Field(default=None, ge=0)


class MedicalProfileRead(MedicalProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
