from datetime import datetime

from pydantic import BaseModel


class DietRecommendationBase(BaseModel):
    daily_caloric_intake_kcal: float | None = None
    adherence_to_diet_plan_pct: float | None = None
    dietary_nutrient_imbalance_score: float | None = None
    recommendation: str | None = None
    recommended_at: datetime


class DietRecommendationCreate(DietRecommendationBase):
    pass


class DietRecommendationRead(DietRecommendationBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
