from datetime import datetime

from pydantic import BaseModel, Field


class FitnessProfileBase(BaseModel):
    physical_activity_level: str | None = None
    workout_frequency_days_per_week: int | None = Field(default=None, ge=0, le=7)
    experience_level: str | None = None
    weekly_exercise_hours: float | None = Field(default=None, ge=0)
    recorded_at: datetime


class FitnessProfileCreate(FitnessProfileBase):
    pass


class FitnessProfileUpdate(BaseModel):
    physical_activity_level: str | None = None
    workout_frequency_days_per_week: int | None = Field(default=None, ge=0, le=7)
    experience_level: str | None = None
    weekly_exercise_hours: float | None = Field(default=None, ge=0)


class FitnessProfileRead(FitnessProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
