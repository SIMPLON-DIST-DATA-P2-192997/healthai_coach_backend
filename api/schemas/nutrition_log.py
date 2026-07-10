from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

MealType = Literal["breakfast", "lunch", "dinner", "snack"]


class NutritionLogBase(BaseModel):
    food_item_id: int
    portion_number: float = Field(gt=0)
    meal_type: MealType
    logged_at: datetime | None = None


class NutritionLogCreate(NutritionLogBase):
    pass


class NutritionLogUpdate(BaseModel):
    portion_number: float | None = Field(default=None, gt=0)
    meal_type: MealType | None = None
    logged_at: datetime | None = None


class NutritionLogRead(NutritionLogBase):
    id: int
    user_id: int
    logged_at: datetime
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
