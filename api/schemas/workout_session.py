from datetime import datetime

from pydantic import BaseModel


class WorkoutSessionBase(BaseModel):
    started_at: datetime
    ended_at: datetime | None = None
    max_bpm: int | None = None
    avg_bpm: int | None = None
    notes: str | None = None


class WorkoutSessionCreate(WorkoutSessionBase):
    pass


class WorkoutSessionUpdate(BaseModel):
    ended_at: datetime | None = None
    max_bpm: int | None = None
    avg_bpm: int | None = None
    notes: str | None = None


class WorkoutSessionRead(WorkoutSessionBase):
    id: int
    user_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
