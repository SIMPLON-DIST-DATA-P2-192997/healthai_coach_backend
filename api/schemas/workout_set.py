from pydantic import BaseModel


class WorkoutSetBase(BaseModel):
    exercise_id: int
    set_number: int | None = None
    reps: int | None = None
    weight_kg: float | None = None
    duration_seconds: int | None = None
    distance_m: float | None = None


class WorkoutSetCreate(WorkoutSetBase):
    pass


class WorkoutSetUpdate(BaseModel):
    set_number: int | None = None
    reps: int | None = None
    weight_kg: float | None = None
    duration_seconds: int | None = None
    distance_m: float | None = None


class WorkoutSetRead(WorkoutSetBase):
    id: int
    session_id: int

    model_config = {"from_attributes": True}
