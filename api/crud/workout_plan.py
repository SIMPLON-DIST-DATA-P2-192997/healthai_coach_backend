from typing import List

from sqlalchemy.orm import Session

from api.models.workout_plan import WorkoutPlan


def get_workout_plans_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[WorkoutPlan]:
    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id)
        .order_by(WorkoutPlan.generated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_workout_plan(db: Session, user_id: int, goal: str | None, plan_text: str) -> WorkoutPlan:
    plan = WorkoutPlan(user_id=user_id, goal=goal, plan_text=plan_text)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
