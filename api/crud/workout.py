from typing import List

from sqlalchemy.orm import Session

from api.models.workout_session import WorkoutSession
from api.models.workout_set import WorkoutSet
from api.schemas.workout_session import WorkoutSessionCreate, WorkoutSessionUpdate
from api.schemas.workout_set import WorkoutSetCreate, WorkoutSetUpdate


# ---------------------------------------------------------------------------
# Workout Sessions
# ---------------------------------------------------------------------------

def get_session(db: Session, session_id: int) -> WorkoutSession | None:
    return db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()


def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[WorkoutSession]:
    return (
        db.query(WorkoutSession)
        .filter(WorkoutSession.user_id == user_id)
        .order_by(WorkoutSession.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_session(db: Session, user_id: int, session_in: WorkoutSessionCreate) -> WorkoutSession:
    session = WorkoutSession(user_id=user_id, **session_in.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_session(db: Session, session: WorkoutSession, update_data: WorkoutSessionUpdate) -> WorkoutSession:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: int) -> bool:
    session = get_session(db, session_id)
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Workout Sets
# ---------------------------------------------------------------------------

def get_set(db: Session, set_id: int) -> WorkoutSet | None:
    return db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()


def get_sets_by_session(db: Session, session_id: int) -> List[WorkoutSet]:
    return db.query(WorkoutSet).filter(WorkoutSet.session_id == session_id).all()


def create_set(db: Session, session_id: int, set_in: WorkoutSetCreate) -> WorkoutSet:
    workout_set = WorkoutSet(session_id=session_id, **set_in.model_dump())
    db.add(workout_set)
    db.commit()
    db.refresh(workout_set)
    return workout_set


def update_set(db: Session, workout_set: WorkoutSet, update_data: WorkoutSetUpdate) -> WorkoutSet:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(workout_set, field, value)
    db.commit()
    db.refresh(workout_set)
    return workout_set


def delete_set(db: Session, set_id: int) -> bool:
    workout_set = get_set(db, set_id)
    if not workout_set:
        return False
    db.delete(workout_set)
    db.commit()
    return True
