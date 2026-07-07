from datetime import datetime

from pydantic import BaseModel


class BiometricMeasurementBase(BaseModel):
    measured_at: datetime
    weight_kg: float | None = None
    height_cm: float | None = None
    body_fat_pct: float | None = None
    muscle_mass_kg: float | None = None
    resting_heart_rate: int | None = None
    source: str | None = None


class BiometricMeasurementCreate(BiometricMeasurementBase):
    pass


class BiometricMeasurementUpdate(BaseModel):
    weight_kg: float | None = None
    height_cm: float | None = None
    body_fat_pct: float | None = None
    muscle_mass_kg: float | None = None
    resting_heart_rate: int | None = None
    source: str | None = None


class BiometricMeasurementRead(BiometricMeasurementBase):
    id: int
    user_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
