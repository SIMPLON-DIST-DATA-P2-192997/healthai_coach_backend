from datetime import datetime

from pydantic import BaseModel


class FoodItemBase(BaseModel):
    external_id: str | None = None
    source: str | None = None
    name: str
    brand: str | None = None
    calories_kcal: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None
    cholesterol_mg: float | None = None
    serving_size_g: float | None = None


class FoodItemCreate(FoodItemBase):
    pass


class FoodItemUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    calories_kcal: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None
    cholesterol_mg: float | None = None
    serving_size_g: float | None = None


class FoodItemRead(FoodItemBase):
    id: int
    ingested_at: datetime | None = None

    model_config = {"from_attributes": True}
