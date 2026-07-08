from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class WorkoutSessionBase(BaseModel):
    started_at: datetime
    ended_at: datetime | None = None
    max_bpm: int | None = Field(default=None, gt=0)
    avg_bpm: int | None = Field(default=None, gt=0)
    notes: str | None = None

    @model_validator(mode="after")
    def _check_ended_after_started(self) -> "WorkoutSessionBase":
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self


class WorkoutSessionCreate(WorkoutSessionBase):
    pass


class WorkoutSessionUpdate(BaseModel):
    ended_at: datetime | None = None
    max_bpm: int | None = Field(default=None, gt=0)
    avg_bpm: int | None = Field(default=None, gt=0)
    notes: str | None = None


class WorkoutSessionRead(WorkoutSessionBase):
    id: int
    user_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
