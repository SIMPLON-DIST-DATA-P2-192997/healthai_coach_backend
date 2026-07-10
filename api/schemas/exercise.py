from datetime import datetime

from pydantic import BaseModel


class ExerciseBase(BaseModel):
    external_id: str | None = None
    source: str | None = None
    name: str
    body_part: str | None = None
    target_muscle: str | None = None
    equipment: str | None = None
    gif_url: str | None = None
    instructions: str | None = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: str | None = None
    body_part: str | None = None
    target_muscle: str | None = None
    equipment: str | None = None
    gif_url: str | None = None
    instructions: str | None = None


class ExerciseRead(ExerciseBase):
    id: int
    ingested_at: datetime | None = None

    model_config = {"from_attributes": True}
