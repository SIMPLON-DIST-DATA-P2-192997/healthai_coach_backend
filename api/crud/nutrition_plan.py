from typing import List

from sqlalchemy.orm import Session

from api.models.nutrition_plan import NutritionPlan


def get_nutrition_plans_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[NutritionPlan]:
    return (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user_id)
        .order_by(NutritionPlan.generated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_nutrition_plan(db: Session, user_id: int, goal: str | None, plan_text: str) -> NutritionPlan:
    plan = NutritionPlan(user_id=user_id, goal=goal, plan_text=plan_text)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
