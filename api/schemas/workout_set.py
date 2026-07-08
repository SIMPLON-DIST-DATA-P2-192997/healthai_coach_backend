from pydantic import BaseModel, Field


class WorkoutSetBase(BaseModel):
    exercise_id: int
    set_number: int = Field(gt=0)
    reps: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)
    distance_m: float | None = Field(default=None, ge=0)


class WorkoutSetCreate(WorkoutSetBase):
    pass


class WorkoutSetUpdate(BaseModel):
    set_number: int | None = Field(default=None, gt=0)
    reps: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)
    distance_m: float | None = Field(default=None, ge=0)


class WorkoutSetRead(WorkoutSetBase):
    id: int
    session_id: int

    model_config = {"from_attributes": True}
