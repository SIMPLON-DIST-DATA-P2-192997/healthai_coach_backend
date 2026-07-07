from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DB
from api.crud.workout import (
    create_session, create_set, delete_session, delete_set,
    get_session, get_sessions_by_user, get_set, get_sets_by_session,
    update_session, update_set,
)
from api.schemas.workout_session import WorkoutSessionCreate, WorkoutSessionRead, WorkoutSessionUpdate
from api.schemas.workout_set import WorkoutSetCreate, WorkoutSetRead, WorkoutSetUpdate

router = APIRouter(prefix="/workouts", tags=["workouts"])


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

@router.get("", response_model=List[WorkoutSessionRead])
def list_my_sessions(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[WorkoutSessionRead]:
    return get_sessions_by_user(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.post("", response_model=WorkoutSessionRead, status_code=status.HTTP_201_CREATED)
def create_my_session(session_in: WorkoutSessionCreate, current_user: CurrentUser, db: DB) -> WorkoutSessionRead:
    return create_session(db, current_user.id, session_in)  # type: ignore[return-value]


@router.get("/{session_id}", response_model=WorkoutSessionRead)
def read_my_session(session_id: int, current_user: CurrentUser, db: DB) -> WorkoutSessionRead:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session  # type: ignore[return-value]


@router.put("/{session_id}", response_model=WorkoutSessionRead)
def update_my_session(
    session_id: int, update_data: WorkoutSessionUpdate, current_user: CurrentUser, db: DB
) -> WorkoutSessionRead:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return update_session(db, session, update_data)  # type: ignore[return-value]


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_session(session_id: int, current_user: CurrentUser, db: DB) -> None:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    delete_session(db, session_id)


# ---------------------------------------------------------------------------
# Sets (nested under sessions)
# ---------------------------------------------------------------------------

@router.get("/{session_id}/sets", response_model=List[WorkoutSetRead])
def list_sets(session_id: int, current_user: CurrentUser, db: DB) -> List[WorkoutSetRead]:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return get_sets_by_session(db, session_id)  # type: ignore[return-value]


@router.post("/{session_id}/sets", response_model=WorkoutSetRead, status_code=status.HTTP_201_CREATED)
def create_set_endpoint(
    session_id: int, set_in: WorkoutSetCreate, current_user: CurrentUser, db: DB
) -> WorkoutSetRead:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return create_set(db, session_id, set_in)  # type: ignore[return-value]


@router.put("/{session_id}/sets/{set_id}", response_model=WorkoutSetRead)
def update_set_endpoint(
    session_id: int, set_id: int, update_data: WorkoutSetUpdate, current_user: CurrentUser, db: DB
) -> WorkoutSetRead:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    workout_set = get_set(db, set_id)
    if not workout_set or int(workout_set.session_id) != session_id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found")
    return update_set(db, workout_set, update_data)  # type: ignore[return-value]


@router.delete("/{session_id}/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set_endpoint(session_id: int, set_id: int, current_user: CurrentUser, db: DB) -> None:
    session = get_session(db, session_id)
    if not session or int(session.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if not delete_set(db, set_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found")
