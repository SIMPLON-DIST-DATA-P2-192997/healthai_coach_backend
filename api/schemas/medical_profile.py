from datetime import datetime

from pydantic import BaseModel


class MedicalProfileBase(BaseModel):
    disease_type: str | None = None
    severity: str | None = None
    cholesterol_mg_dl: float | None = None
    blood_pressure_mmhg: float | None = None
    glucose_mg_dl: float | None = None
    recorded_at: datetime


class MedicalProfileCreate(MedicalProfileBase):
    pass


class MedicalProfileUpdate(BaseModel):
    disease_type: str | None = None
    severity: str | None = None
    cholesterol_mg_dl: float | None = None
    blood_pressure_mmhg: float | None = None
    glucose_mg_dl: float | None = None


class MedicalProfileRead(MedicalProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
