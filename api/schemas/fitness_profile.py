from datetime import datetime

from pydantic import BaseModel


class FitnessProfileBase(BaseModel):
    physical_activity_level: str | None = None
    workout_frequency_days_per_week: int | None = None
    experience_level: str | None = None
    weekly_exercise_hours: float | None = None
    recorded_at: datetime


class FitnessProfileCreate(FitnessProfileBase):
    pass


class FitnessProfileUpdate(BaseModel):
    physical_activity_level: str | None = None
    workout_frequency_days_per_week: int | None = None
    experience_level: str | None = None
    weekly_exercise_hours: float | None = None


class FitnessProfileRead(FitnessProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
