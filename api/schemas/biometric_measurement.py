from datetime import datetime

from pydantic import BaseModel, Field


class BiometricMeasurementBase(BaseModel):
    measured_at: datetime
    weight_kg: float | None = Field(default=None, gt=0)
    height_cm: float | None = Field(default=None, gt=0)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100)
    muscle_mass_kg: float | None = Field(default=None, ge=0)
    resting_heart_rate: int | None = Field(default=None, gt=0)
    source: str | None = None


class BiometricMeasurementCreate(BiometricMeasurementBase):
    pass


class BiometricMeasurementUpdate(BaseModel):
    weight_kg: float | None = Field(default=None, gt=0)
    height_cm: float | None = Field(default=None, gt=0)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100)
    muscle_mass_kg: float | None = Field(default=None, ge=0)
    resting_heart_rate: int | None = Field(default=None, gt=0)
    source: str | None = None


class BiometricMeasurementRead(BiometricMeasurementBase):
    id: int
    user_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
