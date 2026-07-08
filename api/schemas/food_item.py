from datetime import datetime

from pydantic import BaseModel, Field


class FoodItemBase(BaseModel):
    external_id: str | None = None
    source: str
    name: str
    brand: str | None = None
    calories_kcal: float = Field(ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    sugar_g: float | None = Field(default=None, ge=0)
    sodium_mg: float | None = Field(default=None, ge=0)
    cholesterol_mg: float | None = Field(default=None, ge=0)
    serving_size_g: float | None = Field(default=None, gt=0)


class FoodItemCreate(FoodItemBase):
    pass


class FoodItemUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    calories_kcal: float | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    sugar_g: float | None = Field(default=None, ge=0)
    sodium_mg: float | None = Field(default=None, ge=0)
    cholesterol_mg: float | None = Field(default=None, ge=0)
    serving_size_g: float | None = Field(default=None, gt=0)


class FoodItemRead(FoodItemBase):
    id: int
    ingested_at: datetime | None = None

    model_config = {"from_attributes": True}
