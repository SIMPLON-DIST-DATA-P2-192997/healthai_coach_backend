from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from api.models.nutrition_log import NutritionLog
from api.schemas.nutrition_log import NutritionLogCreate, NutritionLogUpdate


def get_nutrition_log(db: Session, log_id: int) -> NutritionLog | None:
    return db.query(NutritionLog).filter(NutritionLog.id == log_id).first()


def get_nutrition_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[NutritionLog]:
    return (
        db.query(NutritionLog)
        .filter(NutritionLog.user_id == user_id)
        .order_by(NutritionLog.logged_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_nutrition_log(db: Session, user_id: int, log_in: NutritionLogCreate) -> NutritionLog:
    data = log_in.model_dump()
    if data.get("logged_at") is None:
        data["logged_at"] = datetime.now(timezone.utc)
    log = NutritionLog(user_id=user_id, **data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_nutrition_log(db: Session, log: NutritionLog, update_data: NutritionLogUpdate) -> NutritionLog:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


def delete_nutrition_log(db: Session, log_id: int) -> bool:
    log = get_nutrition_log(db, log_id)
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True
