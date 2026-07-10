from datetime import datetime

from pydantic import BaseModel


class WorkoutPlanRead(BaseModel):
    id: int
    user_id: int
    goal: str | None = None
    plan_text: str
    generated_at: datetime

    model_config = {"from_attributes": True}
