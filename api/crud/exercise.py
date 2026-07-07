from typing import List

from sqlalchemy.orm import Session

from api.models.exercise import Exercise
from api.schemas.exercise import ExerciseCreate, ExerciseUpdate


def get_exercise(db: Session, exercise_id: int) -> Exercise | None:
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()


def get_exercises(db: Session, skip: int = 0, limit: int = 100) -> List[Exercise]:
    return db.query(Exercise).offset(skip).limit(limit).all()


def create_exercise(db: Session, exercise_in: ExerciseCreate) -> Exercise:
    exercise = Exercise(**exercise_in.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def update_exercise(db: Session, exercise: Exercise, update_data: ExerciseUpdate) -> Exercise:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(exercise, field, value)
    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, exercise_id: int) -> bool:
    exercise = get_exercise(db, exercise_id)
    if not exercise:
        return False
    db.delete(exercise)
    db.commit()
    return True
