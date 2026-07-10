from datetime import datetime

from pydantic import BaseModel


class DietaryPreferenceBase(BaseModel):
    dietary_restrictions: str | None = None
    allergies: str | None = None
    preferred_cuisine: str | None = None
    recorded_at: datetime


class DietaryPreferenceCreate(DietaryPreferenceBase):
    pass


class DietaryPreferenceUpdate(BaseModel):
    dietary_restrictions: str | None = None
    allergies: str | None = None
    preferred_cuisine: str | None = None


class DietaryPreferenceRead(DietaryPreferenceBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
