from datetime import datetime

from pydantic import BaseModel, Field


class DietRecommendationBase(BaseModel):
    daily_caloric_intake_kcal: float | None = Field(default=None, ge=0)
    adherence_to_diet_plan_pct: float | None = Field(default=None, ge=0, le=100)
    dietary_nutrient_imbalance_score: float | None = None
    recommendation: str | None = None
    recommended_at: datetime


class DietRecommendationCreate(DietRecommendationBase):
    pass


class DietRecommendationRead(DietRecommendationBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
