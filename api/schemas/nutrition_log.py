from datetime import datetime

from pydantic import BaseModel


class NutritionLogBase(BaseModel):
    food_item_id: int
    quantity_g: float
    meal_type: str | None = None
    logged_at: datetime | None = None


class NutritionLogCreate(NutritionLogBase):
    pass


class NutritionLogUpdate(BaseModel):
    quantity_g: float | None = None
    meal_type: str | None = None
    logged_at: datetime | None = None


class NutritionLogRead(NutritionLogBase):
    id: int
    user_id: int
    logged_at: datetime
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
